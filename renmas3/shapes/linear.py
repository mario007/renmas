import platform
from ..base import Ray
from .intersector import Intersector
from .hit import HitPoint
from ..macros import create_assembler

class LinearIsect(Intersector):
    def __init__(self, mgr=None):
        self.mgr = mgr

    def prepare(self):
        pass

    def isect(self, ray): #intersection ray with scene
        if self.mgr is None:
            raise ValueError("Shape manager is not set")

        min_dist = 99999999.0
        hit_point = False 
        for shape in self.mgr:
            hit = shape.isect(ray, min_dist)
            if hit is False:
                continue
            if hit.t < min_dist:
                min_dist = hit.t
                hit_point = hit
        return hit_point

    def isect_b(self, ray):
        hit_t = False 
        min_dist = 99999999.0
        for shape in self.mgr:
            t = shape.isect_b(ray, min_dist)
            if t is False:
                continue
            if t < min_dist:
                min_dist = t
                hit_t = t
        return hit_t

    def visibility(self, p1, p2):
        epsilon = 0.00001
        direction = p2 - p1

        distance = direction.length() - epsilon # self intersection!!! visiblity

        ray = Ray(p1, direction.normalize())
        t = self.isect_b(ray)
        if not t:
            return True
        else:
            if t < distance:
                return False
            else:
                return True

    # eax - pointer to ray
    def isect_asm_b(self, runtimes, label):
        self._isect_asm(runtimes, label, visibility=True)

    # eax - pointer to ray
    # ebx - pointer to hitpoint
    def isect_asm(self, runtimes, label):
        self._isect_asm(runtimes, label)

    # eax - pointer to ray
    # ebx - pointer to hitpoint
    def _isect_asm(self, runtimes, label, visibility=False):
        if self.mgr is None:
            raise ValueError("Shape manager is not set")
        data = self._generate_data_section()
        bits = platform.architecture()[0]
        if bits == '64bit':
            code = self._generate_code_section64(runtimes, label, visibility)
        else:
            code = self._generate_code_section32(runtimes, label, visibility)

        assembler = create_assembler()
        mc = assembler.assemble(data+code, True)
        #mc.print_machine_code()
        if not visibility:
            name = "ray_scene_intersection" + str(id(self))
        else:
            name = "ray_scene_intersection_visibility" + str(id(self))
        ds_arr = []
        for r in runtimes:
            if not r.global_exists(label):
                ds_arr.append(r.load(name, mc))

        for shp_type in self.mgr.shape_types():
            dy_arr = self.mgr.dynamic_array(shp_type)
            for ds in ds_arr:
                ds["ptr_" + shp_type.asm_struct_name()] = dy_arr.address_info()
                ds["n_" + shp_type.asm_struct_name()] = dy_arr.size

    def _generate_data_section(self):
        bits = platform.architecture()[0]
        if bits == '64bit':
            data = "uint64 r1, hp \n" 
        else:
            data = "uint32 r1, hp \n" 
        data += """
        float min_dist = 999999.0
        float max_dist = 999999.0
        float zero = 0.0
        float one = 1.0
        float epsilon = 0.00001
        """
        structs = HitPoint.asm_struct() + Ray.asm_struct()
        data2 = "\n"
        for shp_type in self.mgr.shape_types():
            structs += shp_type.asm_struct()
            if bits == '64bit':
                data2 += "uint64 ptr_%s \n" % shp_type.asm_struct_name()
            else:
                data2 += "uint32 ptr_%s \n" % shp_type.asm_struct_name()
            data2 += "uint32 n_%s \n" % shp_type.asm_struct_name()

        data = "#DATA\n" + structs + data + data2
        return data

    # eax - pointer to ray
    # ebx - pointer to hitpoint
    def _generate_code_section32(self, runtimes, label, visibility):
        ASM = "#CODE \n"
        ASM += "global " + label + ":\n"
        ASM += """
            mov dword [r1], eax
            mov edx , dword [zero]
            macro eq32 min_dist = max_dist + one {xmm0}
        """
        if not visibility:
            ASM += """
            mov dword [hp], ebx
            mov dword [ebx + Hitpoint.t], edx
            """
        code = ""
        for shp_type in self.mgr.shape_types():
            code1 = """ 
            ;=== intersection of array
            mov eax, dword [r1]
            mov ebx, dword [hp]
            mov ecx, min_dist
            """
            line1 = "mov esi, dword [" + "ptr_" + shp_type.asm_struct_name() + "] \n"
            line2 = "mov edi, dword [" + "n_" + shp_type.asm_struct_name() + "]\n"
            if not visibility:
                call = "call " + shp_type.asm_struct_name() + "_array \n"
            else:
                call = "call " + shp_type.asm_struct_name() + "_array_bool \n"
            code = code1 + line1 + line2 + call
            ASM += code
            
            if not visibility:
                lbl_isect = shp_type.asm_struct_name() + "_intersect"
                shp_type.isect_asm(runtimes, lbl_isect)
                self._isect_ray_shape_array_asm(shp_type, runtimes, shp_type.asm_struct_name() + '_array', lbl_isect)
            else:
                lbl_isect = shp_type.asm_struct_name() + "_intersect_bool"
                shp_type.isect_asm_b(runtimes, lbl_isect)
                self._isect_ray_shape_array_asm(shp_type, runtimes, shp_type.asm_struct_name() + '_array_bool', lbl_isect, True)
        
        ASM += """
            macro eq32 xmm0 = min_dist
            macro if xmm0 < max_dist goto _accept
            mov eax, 0
            ret

            _accept:
            macro if xmm0 < epsilon goto _reject
            mov eax, 1
            ret
            _reject:
            mov eax, 0
            ret
        """
        return ASM 

    # eax - ray
    # ebx - hitpoint
    # ecx - min_dist
    # esi - ptr_array
    # edi - nshapes 
    def _isect_ray_shape_array_asm(self, typ_shape, runtimes, isect_ray_shapes, isect_ray_shape, visibility=False):
        bits = platform.architecture()[0]
        if bits == '64bit':
            ASM = self._isect_ray_shape_array_asm_code64(typ_shape, isect_ray_shapes, isect_ray_shape, visibility)
        else:
            ASM = self._isect_ray_shape_array_asm_code32(typ_shape, isect_ray_shapes, isect_ray_shape, visibility)

        assembler = create_assembler()
        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        func_name = "isect_ray_array" + str(id(typ_shape))
        for r in runtimes:
            if not r.global_exists(isect_ray_shapes):
                r.load(func_name, mc)

    def _isect_ray_shape_array_asm_code32(self, typ_shape, isect_ray_shapes, isect_ray_shape, visibility):

        ASM = "#DATA \n" + HitPoint.asm_struct() + typ_shape.asm_struct() +"  #CODE \n "

        ASM += " global " + isect_ray_shapes + ":\n" + """
          ; eax - ray, ebx - hp , ecx - min_dist, esi - ptr_array, edi - nshapes
        push ecx
        push eax
        push ebx
        push esi
        push edi
        

        _objects_loop:
        mov eax, dword [esp + 12] ; mov eax, ray
        mov ebx, dword [esp + 4] ; mov ebx, shape 
        mov ecx, dword [esp + 16]; address of minimum distance
        """
        if not visibility:
            ASM += " mov edx, dword [esp + 8] ; mov edx, hp \n "

        ASM += " call " + isect_ray_shape + "\n" + """
        cmp eax, 0  ; 0 - no intersection ocur
        je _next_object
        """
        if not visibility:
            ASM += """
                mov eax, dword [esp + 8]
                mov ebx, dword [eax + Hitpoint.t]

                mov edx, dword [esp + 16] ;populate new minimum distance
                mov dword [edx], ebx
                """
        else:
            ASM += """
                mov edx, dword [esp + 16] ;populate new minimum distance
                macro eq32 edx = xmm0 {xmm0}
            """

        ASM += """
        _next_object:
        sub dword [esp], 1  
        jz _end_objects
        """
        ASM += "add dword [esp + 4], sizeof " + typ_shape.asm_struct_name() + "\n" + """ 
        jmp _objects_loop
        
        _end_objects:
        add esp, 20 
        ret
        """
        return ASM

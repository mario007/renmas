
import platform

from .logger import log
from .dynamic_array import DynamicArray
from .ray import Ray
from .structures import SHADEPOINT, RAY 

class ShapeManager:
    def __init__(self, renderer):
        self._renderer = renderer

        self._strategy = False # False means linear intersection, True using Grids 
        self._ready = False
        #self._grid = Grid()

        self._shape_names = {} #name:shape
        self._shape_addr = {} # shape:idx  - using index in dynamic array we can calculate address
        self._shape_arrays = {} # DynamicArrays for assembly rendering

    def prepare(self): #build acceleration structure
        if not self._ready:
            self._lst_shapes = list(self._shape_names.values())
            if self._strategy: #create grid structure  
                if len(self._lst_shapes) > 0:
                    self._grid.setup(self._lst_shapes)
            self._ready = True

    def set_strategy(self, strategy):
        if strategy == 'grid':
            self._strategy = True 
        else:
            self._strategy = False
        self._ready = False 

    def names(self):
        return self._shape_names.keys()

    def shape(self, name):
        if name in self._shape_names:
            return self._shape_names[name]
        return None

    def add(self, name, shape):
        if name in self._shape_names:
            log.info("Shape with that " + name + " allready exist!!!")
            return
        #TODO Check if shape has valid material - put default it it doesn't have
        self._shape_names[name] = shape #name:shape
        # Tip: Be very carefull - dynamic arrays do automatic resize by himself
        if type(shape) not in self._shape_arrays:
            darr = DynamicArray(shape.compiled_struct())
            self._shape_arrays[type(shape)] = darr
            idx = 0
        else:
            darr = self._shape_arrays[type(shape)]
            idx = darr.num_objects()

        darr.add_instance(shape.attributes())
        self._shape_addr[shape] = idx 
        self._ready = False 

    def remove(self, name): #TODO
        pass

    def update(self, shape):
        try:
            idx = self._shape_addr[shape]
            darr = self._shape_arrays[type(shape)]
            darr.edit_instance(idx, shape.attributes())
            self._ready = False 
        except:
            log.info("Cannot update shape because shape doesn't exist!")

    def update_material(self, shape):
        try:
            idx = self._shape_addr[shape]
            darr = self._shape_arrays[type(shape)]
            darr.edit_instance(idx, shape.attributes())
        except:
            log.info("Cannot update shape because shape doesn't exist!")

    def address_info(self, shape):
        idx = self._shape_addr.get(shape, None)
        if idx is None: 
            log.info("Cannot return address of Shape because shape doesn't exist!")
            return None

        darr = self._shape_arrays[type(shape)]
        addr = darr.address_info() + idx * darr.obj_size() 
        return addr

    def isect(self, ray): #intersection ray with scene
        if self._strategy:
            if len(self._lst_shapes) > 0:
                return self._grid.isect(ray)
            else:
                return self._linear_isect(ray)
        else:
            return self._linear_isect(ray)

    def _isect_visibility(self, ray): #intersection ray with scene
        if self._strategy:
            if len(self._lst_shapes) > 0:
                return self._grid.isect_b(ray)
            else:
                return self._linear_isect_visibility(ray)
        else:
            return self._linear_isect_visibility(ray)

    def _linear_isect_visibility(self, ray, min_dist=999999.0):
        hit_t = False 
        for s in self._lst_shapes:
            t = s.isect_b(ray, min_dist)
            if t is False: continue
            if t < min_dist:
                min_dist = t
                hit_t = t
        return hit_t

    def _linear_isect(self, ray, min_dist=999999.0):
        hit_point = False 
        for s in self._lst_shapes:
            hit = s.isect(ray, min_dist)
            if hit is False: continue
            if hit.t < min_dist:
                min_dist = hit.t
                hit_point = hit
        return hit_point

    def visibility(self, p1, p2):
        epsilon = 0.00001
        direction = p2 - p1

        distance = direction.length() - epsilon # self intersection!!! visiblity

        ray = Ray(p1, direction.normalize())
        t = self._isect_visibility(ray)
        if not t: return True
        else:
            if t < distance:
                return False
            else:
                return True
    
    def isect_asm(self, runtimes, label):
        if self._strategy:
            if len(self._lst_shapes) > 0:
                ren = self.renderer
                self._grid.isect_asm(runtimes, label, ren.assembler, ren.structures, self._shape_arrays, self)
            else:
                self._isect_ray_scene_asm(runtimes, label)
        else:
            self._isect_ray_scene_asm(runtimes, label)

    # eax - pointer to ray
    # ebx - pointer to hitpoint
    def _isect_ray_scene_asm(self, runtimes, label, visibility=False):
        data = self._generate_data_section()
        bits = platform.architecture()[0]
        if bits == '64bit':
            code = self._generate_code_section64(runtimes, label, visibility)
        else:
            code = self._generate_code_section32(runtimes, label, visibility)

        mc = self._renderer.assembler.assemble(data+code, True)
        #mc.print_machine_code()
        if not visibility:
            name = "ray_scene_intersection" + str(id(self))
        else:
            name = "ray_scene_intersection_visibility" + str(id(self))
        
        ds_arr = []
        for r in runtimes:
            if not r.global_exists(label):
                ds_arr.append(r.load(name, mc))

        for key, value in self._shape_arrays.items():
            dy_arr = self._shape_arrays[key]
            for ds in ds_arr:
                ds["ptr_" + key.name()] = dy_arr.address_info()
                ds["n_" + key.name()] = dy_arr.size

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
        structs = self._renderer.color_mgr.spectrum_struct() + SHADEPOINT
        data2 = "\n"
        for key, value in self._shape_arrays.items():
            structs += key.struct()
            if bits == '64bit':
                data2 += "uint64 ptr_%s \n" % key.name()
            else:
                data2 += "uint32 ptr_%s \n" % key.name()
            data2 += "uint32 n_%s \n" % key.name()

        data = "#DATA\n" + structs + data + data2
        return data
    
    # eax - pointer to ray
    # ebx - pointer to shadepoint 
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
            mov dword [ebx + shadepoint.t], edx
            """
        code = ""
        for key, value in self._shape_arrays.items():
            code1 = """ 
            ;=== intersection of array
            mov eax, dword [r1]
            mov ebx, dword [hp]
            mov ecx, min_dist
            """
            line1 = "mov esi, dword [" + "ptr_" + key.name() + "] \n"
            line2 = "mov edi, dword [" + "n_" + key.name() + "]\n"
            if not visibility:
                call = "call " + key.name() + "_array \n"
            else:
                call = "call " + key.name() + "_array_bool \n"
            code = code1 + line1 + line2 + call
            ASM += code
            
            ren = self._renderer
            if not visibility:
                key.isect_asm(runtimes, key.name() + "_intersect", ren.assembler, ren.color_mgr.spectrum_struct())
                self._isect_ray_shape_array_asm(key, runtimes, key.name() + '_array', key.name() + '_intersect')
            else:
                key.isect_asm_b(runtimes, key.name() + "_intersect_bool", ren.assembler)
                self._isect_ray_shape_array_asm(key, runtimes, key.name() + '_array_bool', key.name() + '_intersect_bool', True)
        
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

    # rax - pointer to ray
    # rbx - pointer to shadepoint 
    def _generate_code_section64(self, runtimes, label, visibility):
        ASM = "#CODE \n"
        ASM += "global " + label + ":\n"
        ASM += """
            mov qword [r1], rax
            mov edx , dword [zero]
            macro eq32 min_dist = max_dist + one {xmm0}
        """
        if not visibility:
            ASM += """
            mov qword [hp], rbx
            mov dword [rbx + shadepoint.t], edx
            """
        code = ""
        for key, value in self._shape_arrays.items():
            code1 = """ 
            ;=== intersection of array
            mov rax, qword [r1]
            mov rbx, qword [hp]
            mov rcx, min_dist
            """
            line1 = "mov rsi, qword [" + "ptr_" + key.name() + "] \n"
            line2 = "mov edi, dword [" + "n_" + key.name() + "]\n"
            if not visibility:
                call = "call " + key.name() + "_array \n"
            else:
                call = "call " + key.name() + "_array_bool \n"
            code = code1 + line1 + line2 + call
            ASM += code
            
            ren = self._renderer
            if not visibility:
                key.isect_asm(runtimes, key.name() + "_intersect", ren.assembler, ren.color_mgr.spectrum_struct())
                self._isect_ray_shape_array_asm(key, runtimes, key.name() + '_array', key.name() + '_intersect')
            else:
                key.isect_asm_b(runtimes, key.name() + "_intersect_bool", ren.assembler)
                self._isect_ray_shape_array_asm(key, runtimes, key.name() + '_array_bool', key.name() + '_intersect_bool', True)
        
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

        mc = self._renderer.assembler.assemble(ASM, True)
        #mc.print_machine_code()
        func_name = "isect_ray_array" + str(id(self))
        for r in runtimes:
            if not r.global_exists(isect_ray_shapes):
                r.load(func_name, mc)

    def _isect_ray_shape_array_asm_code32(self, typ_shape, isect_ray_shapes, isect_ray_shape, visibility):

        ASM = "#DATA \n" + self._renderer.color_mgr.spectrum_struct() + SHADEPOINT + typ_shape.struct() +"  #CODE \n "

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
                mov ebx, dword [eax + shadepoint.t]

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
        ASM += "add dword [esp + 4], sizeof " + typ_shape.name() + "\n" + """ 
        jmp _objects_loop
        
        _end_objects:
        add esp, 20 
        ret
        """
        return ASM

    def _isect_ray_shape_array_asm_code64(self, typ_shape, isect_ray_shapes, isect_ray_shape, visibility=False):
        ASM = "#DATA \n" + self._renderer.color_mgr.spectrum_struct() + SHADEPOINT + typ_shape.struct() +"  #CODE \n "

        ASM += " global " + isect_ray_shapes + ":\n" + """
          ; rax - ray, rbx - hp , rcx - min_dist, rsi - ptr_array, edi - nshapes
        push rcx
        push rax
        push rbx
        push rsi
        push rdi
        

        _objects_loop:
        mov rax, qword [rsp + 24] ; mov eax, ray
        mov rbx, qword [rsp + 8] ; mov ebx, shape 
        mov rcx, qword [rsp + 32]; address of minimum distance
        """
        if not visibility:
            ASM += " mov rdx, qword [esp + 16] ; mov edx, hp \n "

        ASM += " call " + isect_ray_shape + "\n" + """
        cmp eax, 0  ; 0 - no intersection ocur
        je _next_object
        """
        if not visibility:
            ASM += """
                mov rax, qword [rsp + 16]
                mov ebx, dword [rax + shadepoint.t]

                mov rdx, qword [rsp + 32] ;populate new minimum distance
                mov dword [rdx], ebx
                """
        else:
            ASM += """
                mov rdx, qword [rsp + 32] ;populate new minimum distance
                macro eq32 edx = xmm0 {xmm0}
            """

        ASM += """
        _next_object:
        sub dword [rsp], 1  
        jz _end_objects
        """
        ASM += "add qword [rsp + 8], sizeof " + typ_shape.name() + "\n" + """ 
        jmp _objects_loop
        
        _end_objects:
        add rsp, 40 
        ret
        """
        return ASM

    def visibility_asm(self, runtimes, label):
        # visibility of two points # xmm0 = p1  xmm1 = p2
        # xmm0 -- return value minimum distance

        if self._strategy:
            if len(self._lst_shapes) > 0:
                ren = self._renderer
                self._grid.isect_asm_b(runtimes, "__ray_scene_intersection_visibility__", ren.assembler, ren.structures, self._shape_arrays, self)
            else:
                self._isect_ray_scene_asm(runtimes, "__ray_scene_intersection_visibility__", True)
        else:
            self._isect_ray_scene_asm(runtimes, "__ray_scene_intersection_visibility__", True)

        asm_structs = RAY 

        ASM = """
        #DATA
        """
        ASM += asm_structs + """
        ray r1
        float distance
        float epsilon = 0.0005
        #CODE
        """
        ASM += " global " + label + ":\n" + """
        macro eq128 xmm1 = xmm1 - xmm0 
        macro eq128 r1.origin = xmm0 {xmm0} 
        macro eq128 xmm5 = xmm1
        macro dot xmm0 = xmm1 * xmm1 {xmm2, xmm3} 
        macro call sqrtss xmm0 = xmm0
        macro eq32 distance = xmm0 - epsilon {xmm2}
        macro normalization xmm5 {xmm6, xmm7}
        macro eq128 r1.dir = xmm5 {xmm2}
        
        ; call ray scene intersection
        macro mov eax, r1
        call __ray_scene_intersection_visibility__

        cmp eax, 0
        jne _maybe_visible
        ;no intersection ocure that mean that points are visible
        mov eax, 1 
        ret

        _maybe_visible:
        macro if xmm0 > distance goto accept
        xor eax, eax 
        ret
        
        accept:
        mov eax, 1
        ret

        """

        mc = self._renderer.assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "isect_ray_scene_visible" + str(id(self))
        for r in runtimes:
            if not r.global_exists(label):
                r.load(name, mc)


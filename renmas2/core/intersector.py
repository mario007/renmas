
from .ray import Ray
from .logger import log
from .dynamic_array import DynamicArray
from ..shapes import Grid

# add ready attribut ???? TODO -- so we can allways call isect
# when call isect if ready is False call prepare TODO --- think???

class Intersector:
    def __init__(self, renderer):
        self.renderer = renderer
        self.strategy = True # False means linear intersection, True using Grids 
        self._grid = Grid()

        self._shape_names = {} #name:shape
        self._shape_addr = {} # shape:idx  - using index in dynamic array we can calculate address
        self._shape_arrays = {} # DynamicArrays for assembly rendering

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
            darr = DynamicArray(self.renderer.structures.get_compiled_struct(shape.name()))
            self._shape_arrays[type(shape)] = darr
            idx = 0
        else:
            darr = self._shape_arrays[type(shape)]
            idx = darr.num_objects()

        darr.add_instance(shape.attributes())
        self._shape_addr[shape] = idx 

    def remove(self, name):
        pass

    def update(self, shape):
        try:
            idx = self._shape_addr[shape]
            darr = self._shape_arrays[type(shape)]
            darr.edit_instance(idx, shape.attributes())
        except:
            log.info("Cannot update shape because shape doesn't exist!")

    def address_off(self, shape):
        idx = self._shape_addr.get(shape, None)
        if idx is None: 
            log.info("Cannot return address of Shape because it doesn't exist!")
            return None

        darr = self._shape_arrays[type(shape)]
        addr = darr.get_addr() + idx * darr.obj_size() 
        return addr

    def isect(self, ray): #intersection ray with scene
        if self.strategy:
            if len(self._lst_shapes) > 0:
                return self._grid.isect(ray)
            else:
                return self._linear_isect(ray)
        else:
            return self._linear_isect(ray)

    def _isect_visibility(self, ray): #intersection ray with scene
        if self.strategy:
            if len(self._lst_shapes) > 0:
                return self._grid.isect_b(ray)
            else:
                return self._linear_isect_visibility(ray)
        else:
            return self._linear_isect_visibility(ray)

    def isect_asm(self, runtimes, label):
        if self.strategy:
            ren = self.renderer
            self._grid.isect_asm(runtimes, label, ren.assembler, ren.structures, self._shape_arrays, self)
        else:
            self._isect_ray_scene(runtimes, label, self._shape_arrays)

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

    def visibility_asm(self, runtimes, label):
        # visibility of two points # xmm0 = p1  xmm1 = p2
        # xmm0 -- return value minimum distance

        if self.strategy:
            ren = self.renderer
            self._grid.isect_asm_b(runtimes, "__ray_scene_intersection_visibility__", ren.assembler, ren.structures, self._shape_arrays, self)
        else:
            self._isect_ray_scene(runtimes, "__ray_scene_intersection_visibility__", self._shape_arrays, True)

        asm_structs =  self.renderer.structures.structs(('ray',))

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
        mov eax, r1
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

        mc = self.renderer.assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "isect_ray_scene_visible" + str(hash(self))
        for r in runtimes:
            if not r.global_exists(label):
                r.load(name, mc)

    def prepare(self): #build acceleration structure
        if self.strategy:  
            self._lst_shapes = list(self._shape_names.values())
            if len(self._lst_shapes) > 0:
                self._grid.setup(self._lst_shapes)
        else:
            self._lst_shapes = list(self._shape_names.values())

    def set_strategy(self, strategy):
        if strategy == 'grid':
            self.strategy = True 
        else:
            self.strategy = False

    # eax - ray
    # ebx - hitpoint
    # ecx - min_dist
    # esi - ptr_array
    # edi - nshapes 
    def _isect_ray_shape_array_asm(self, name, runtimes, isect_ray_shapes, isect_ray_shape, visibility=False):
        ASM = """
        #DATA
        """
        ASM += self.renderer.structures.structs(('ray', name, 'hitpoint')) + """
        #CODE
        """
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
                mov ebx, dword [eax + hitpoint.t]

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
        ASM += "add dword [esp + 4], sizeof " + name + "\n" + """ 
        jmp _objects_loop
        
        _end_objects:
        add esp, 20 
        ret
        """

        mc = self.renderer.assembler.assemble(ASM, True)
        #mc.print_machine_code()
        func_name = "isect_ray_array" + str(hash(self))
        for r in runtimes:
            if not r.global_exists(isect_ray_shapes):
                r.load(func_name, mc)

    # eax - pointer to ray
    # ebx - pointer to hitpoint
    def _isect_ray_scene(self, runtimes, label, dyn_arrays, visibility=False):

        data1 = """
        uint32 r1
        uint32 hp
        float min_dist = 999999.0
        float max_dist = 999999.0
        float zero = 0.0
        float one = 1.0
        float epsilon = 0.00001
        """
        asm_structs = self.renderer.structures.structs(('ray', 'hitpoint')) 
        data2 = ""
        for key, value in dyn_arrays.items():
            asm_structs += self.renderer.structures.structs((key.name(),)) 
            data2 += "uint32 ptr_" + key.name() + "\n"
            data2 += "uint32 n_" + key.name() + "\n"

        ASM = """
        #DATA
        """
        ASM += asm_structs + data1 + data2
        ASM += "#CODE \n"
        ASM += "global " + label + ":\n"
        ASM += """
            mov dword [r1], eax
            mov edx , dword [zero]
            macro eq32 min_dist = max_dist + one {xmm0}
        """
        if not visibility:
            ASM += """
            mov dword [hp], ebx
            mov dword [ebx + hitpoint.t], edx
            """
        code = ""
        for key, value in dyn_arrays.items():
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

            if not visibility:
                key.isect_asm(runtimes, key.name() + "_intersect", self.renderer.assembler, self.renderer.structures)
                self._isect_ray_shape_array_asm(key.name(), runtimes, key.name() + '_array', key.name() + '_intersect')
            else:
                key.isect_asm_b(runtimes, key.name() + "_intersect_bool", self.renderer.assembler, self.renderer.structures)
                self._isect_ray_shape_array_asm(key.name(), runtimes, key.name() + '_array_bool', key.name() + '_intersect_bool', True)
        
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
        
        mc = self.renderer.assembler.assemble(ASM, True)
        #mc.print_machine_code()
        if not visibility:
            name = "ray_scene_intersection" + str(hash(self))
        else:
            name = "ray_scene_intersection_visibility" + str(hash(self))
        
        ds_arr = []
        for r in runtimes:
            if not r.global_exists(label):
                ds_arr.append(r.load(name, mc))

        for key, value in dyn_arrays.items():
            dy_arr = dyn_arrays[key]
            for ds in ds_arr:
                ds["ptr_" + key.name()] = dy_arr.get_addr()
                ds["n_" + key.name()] = dy_arr.size


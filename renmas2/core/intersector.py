
from .ray import Ray
from .logger import log
from .dynamic_array import DynamicArray

class Intersector:
    def __init__(self, renderer):
        self.renderer = renderer
        self.strategy = False # False means linear intersection, True using Grids 

        self._shape_names = {} #name:shape
        self._shape_addr = {} # shape:idx  - using index in dynamic array we can calculate address
        self._shape_arrays = {} # DynamicArrays for assembly rendering

    def shape(self, name):
        if name in self._shape_names:
            return self._shape_names[name]
        return None

    def add(self, name, shape):
        if name in self._shape_names:
            log.info("Shape with that name allready exist!!!")
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
            log.info("Shape doesn't exist!")
            return None

        darr = self._shape_arrays[type(shape)]
        addr = darr.get_addr() + idx * darr.obj_size() 
        return addr

    def isect(self, ray): #intersection ray with scene
        if self.strategy:
            raise ValueError('Grids are not yet implemented.')
        else:
            return self._linear_isect(ray)

    def isect_asm(self, runtimes, label, assembler, structures):
        if self.strategy:
            raise ValueError('Grids are not yet implemented.')
        else:
            self._isect_ray_scene(runtimes, label, self._shape_arrays, assembler, structures)

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
        hp = self.isect(ray)

        if not hp:
            return True
        else:
            if hp.t < distance:
                return False
            else:
                return True

    def visibility_asm(self, runtimes, label):
        pass

    def prepare(self): #build acceleration structure
        if self.strategy:  
            pass #build grid
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
    def _isect_ray_shape_array_asm(self, name, runtimes, isect_ray_shapes, isect_ray_shape, assembler, structures):
        ASM = """
        #DATA
        """
        ASM += structures.structs(('ray', name, 'hitpoint')) + """
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
        mov edx, dword [esp + 8] ; mov edx, hp
        """
        ASM += " call " + isect_ray_shape + "\n" + """
        cmp eax, 0  ; 0 - no intersection ocur
        je _next_object
        mov eax, dword [esp + 8]
        mov ebx, dword [eax + hitpoint.t]

        mov edx, dword [esp + 16] ;populate new minimum distance
        mov dword [edx], ebx

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

        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        func_name = "isect_ray_array" + str(hash(self))
        for r in runtimes:
            if not r.global_exists(isect_ray_shapes):
                r.load(func_name, mc)


    # eax - pointer to ray
    # ebx - pointer to hitpoint
    def _isect_ray_scene(self, runtimes, label, dyn_arrays, assembler, structures):

        data1 = """
        uint32 r1
        uint32 hp
        float min_dist = 999999.0
        float max_dist = 999999.0
        float zero = 0.0
        float one = 1.0
        float epsilon = 0.00001
        """
        asm_structs = structures.structs(('ray', 'hitpoint')) 
        data2 = ""
        for key, value in dyn_arrays.items():
            asm_structs += structures.structs((key.name(),)) 
            data2 += "uint32 ptr_" + key.name() + "\n"
            data2 += "uint32 n_" + key.name() + "\n"

        ASM = """
        #DATA
        """
        ASM += asm_structs
        ASM += data1
        ASM += data2
        ASM += "#CODE \n"
        ASM += "global " + label + ":\n"
        ASM += "mov dword [r1], eax \n"
        ASM += "mov dword [hp], ebx \n"
        ASM += "mov edx , dword [zero] \n"
        ASM += "macro eq32 min_dist = max_dist + one {xmm0}\n"
        ASM += "mov dword [ebx + hitpoint.t], edx \n"
        
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
            call = "call " + key.name() + "_array \n"
            code = code1 + line1 + line2 + call
            ASM += code

            key.isect_asm(runtimes, key.name() + "_intersect", assembler, structures)
            self._isect_ray_shape_array_asm(key.name(), runtimes, key.name() + '_array', key.name() + '_intersect', assembler, structures)
        
        ASM += "macro eq32 xmm0 = min_dist \n" 
        ASM += "macro if xmm0 < max_dist goto _accept\n"
        ASM += "mov eax, 0\n"
        ASM += "ret \n"

        ASM += "_accept: \n"
        ASM += "macro if xmm0 < epsilon goto _reject\n"
        ASM += "mov eax, 1 \n"
        ASM += "ret\n"
        ASM += "_reject:\n"
        ASM += "mov eax, 0\n"
        ASM += "ret\n"

        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "ray_scene_intersection" + str(hash(self))

        ds_arr = []
        for r in runtimes:
            if not r.global_exists(label):
                ds_arr.append(r.load(name, mc))

        for key, value in dyn_arrays.items():
            dy_arr = dyn_arrays[key]
            for ds in ds_arr:
                ds["ptr_" + key.name()] = dy_arr.get_addr()
                ds["n_" + key.name()] = dy_arr.size


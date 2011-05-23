
import renmas.core
import renmas.utils as util

def intersect_ray_shape_array(name_struct, runtime, lbl_arr_intersect, lbl_ray_intersect):
    
    asm_structs = util.structs("ray", name_struct, "hitpoint")

    ASM = """
    #DATA
    """
    ASM += asm_structs + """
    #CODE
    """
    ASM += " global " + lbl_arr_intersect + ":\n" + """
      ; eax - ray, ebx - hp , ecx - min_dist, esi - ptr_planes, edi - nplanes
    push ecx
    push eax
    push ebx
    push esi
    push edi

    _objects_loop:
    mov eax, dword [esp + 12] ; mov eax, ray
    mov ebx, dword [esp + 4] ; mov ebx, plane 
    mov ecx, dword [esp + 16]; address of minimum distance
    mov edx, dword [esp + 8] ; mov edx, hp
    """
    ASM += " call " + lbl_ray_intersect + "\n" + """
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
    ASM += "add dword [esp + 4], sizeof " + name_struct + "\n" + """ 
    jmp _objects_loop
    
    _end_objects:
    add esp, 20 
    ret
    """

    assembler = util.get_asm()
    mc = assembler.assemble(ASM, True)
    #mc.print_machine_code()
    runtime.load(lbl_arr_intersect, mc)

def isect(ray, shapes, min_dist=999999.0):
    hit_point = None
    for s in shapes:
        hit = s.isect(ray, min_dist)
        if hit is False: continue
        if hit.t < min_dist:
            min_dist = hit.t
            hit_point = hit
    return hit_point

def isect_ray_scene(ray):
    return isect(ray, renmas.core.scene.shape_database.shapes())

def linear_isect_asm(runtime, label_name):
    #FIXME test if there are no shapes and return somethin useful
    db_shapes = renmas.core.scene.shape_database
    db_shapes.create_asm_arrays()

    data1 = """
    uint32 r1
    uint32 hp
    float min_dist = 999999.0
    float max_dist = 999999.0
    float zero = 0.0
    float epsilon = 0.0001
    """

    ASM = """
    #DATA
    """

    asm_structs = util.structs("ray", "hitpoint") 
    data2 = ""
    for key, value in db_shapes.asm_shapes.items():
        asm_structs += util.structs(key.name())
        data2 += "uint32 ptr_" + key.name() + "\n"
        data2 += "uint32 n_" + key.name() + "\n"

    ASM += asm_structs
    ASM += data1
    ASM += data2
    ASM += "#CODE \n"
    ASM += "global " + label_name + ":\n"
    ASM += "mov dword [r1], eax \n"
    ASM += "mov dword [hp], ebx \n"
    ASM += "mov edx , dword [zero] \n"
    ASM += "mov ecx, dword [max_dist] \n"
    ASM += "mov dword [eax + hitpoint.t], edx \n"
    ASM += "mov dword [min_dist], ecx \n"
    
    
    code = ""
    for key, value in db_shapes.asm_shapes.items():
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

        key.intersect_asm(runtime, key.name() + "_intersect")
        intersect_ray_shape_array(key.name(), runtime, key.name() + "_array", key.name() + "_intersect")
    
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
    asm = util.get_asm()
    mc = asm.assemble(ASM, True)
    ds = runtime.load("ray_scene_intersection", mc)

    for key, value in db_shapes.asm_shapes.items():
        dy_arr = db_shapes.asm_shapes[key]
        ds["ptr_" + key.name()] = dy_arr.get_addr()
        ds["n_" + key.name()] = dy_arr.size

    #print (ASM)


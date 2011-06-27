
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

# eax - pointer to ray
# ebx - pointer to hitpoint

def linear_isect_asm(runtime, label, dyn_arrays):

    data1 = """
    uint32 r1
    uint32 hp
    float min_dist = 999999.0
    float max_dist = 999999.0
    float zero = 0.0
    float one = 1.0
    float epsilon = 0.0001
    """

    ASM = """
    #DATA
    """

    asm_structs = util.structs("ray", "hitpoint") 
    data2 = ""
    for key, value in dyn_arrays.items():
        asm_structs += util.structs(key.name())
        data2 += "uint32 ptr_" + key.name() + "\n"
        data2 += "uint32 n_" + key.name() + "\n"

    ASM += asm_structs
    ASM += data1
    ASM += data2
    ASM += "#CODE \n"
    ASM += "global " + label + ":\n"
    ASM += "mov dword [r1], eax \n"
    ASM += "mov dword [hp], ebx \n"
    ASM += "mov edx , dword [zero] \n"
    ASM += "macro eq32 min_dist = max_dist + one\n"
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

        key.isect_asm(runtime, key.name() + "_intersect")
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
    #mc.print_machine_code()
    name = "ray_scene_intersection" + str(util.unique())
    ds = runtime.load(name, mc)

    for key, value in dyn_arrays.items():
        dy_arr = dyn_arrays[key]
        ds["ptr_" + key.name()] = dy_arr.get_addr()
        ds["n_" + key.name()] = dy_arr.size

    #print (ASM)

geometry = renmas.geometry
def lst_shapes():
    return geometry.shapes()

def visible(p1, p2):

    lst_objects = lst_shapes()
    epsilon = 0.00001
    direction = p2 - p1

    distance = direction.length() - epsilon # self intersection!!! visiblity

    ray = renmas.core.Ray(p1, direction.normalize())
    hp = isect(ray, lst_objects, 999999.0)

    if hp is None or hp is False:
        return True
    else:
        if hp.t < distance:
            return False
        else:
            return True

#FIXME - implement so that we can provide distance to ray_scene intersection it will be faster 
def visible_asm(runtime, label, ray_scene_isect):
    # visibility of two points
    # xmm0 = p1
    # xmm1 = p2
    norm = util.normalization("xmm1", "xmm2", "xmm3") 
    asm_structs = util.structs("ray", "hitpoint")

    xmm = "xmm1"
    tmp1 = "xmm2"
    line1 = line2 = line3 = ""
    if util.AVX:
        line1 = "vdpps " + tmp1 + "," + xmm + "," +  xmm + ", 0x7f \n"
        line2 = "vsqrtps " + tmp1 + "," + tmp1 + "\n"
    elif util.SSE41:
        line1 = "movaps " + tmp1 + "," +  xmm + "\n"
        line2 = "dpps " + tmp1 + "," +  tmp1 + ", 0x7F\n" 
        line3 = "sqrtps " + tmp1 + "," + tmp1 + "\n"
    else:
        line1 = "macro dot " + tmp1 + " = " + xmm + "*" + xmm + "\n"
        line2 = "macro broadcast " + tmp1 + " = " + tmp1 + "[0]\n"
        line3 = "sqrtps " + tmp1 + "," + tmp1 + "\n"

    code = line1 + line2 + line3

    ASM = """
    #DATA
    """
    ASM += asm_structs + """
    hitpoint hp
    ray r1
    float distance
    float epsilon = 0.0005

    #CODE
    """
    ASM += " global " + label + ":\n" + """
    macro eq128 xmm1 = xmm1 - xmm0
    macro eq128 r1.origin = xmm0 
    """
    ASM += code + """
    macro eq32 distance = xmm2 - epsilon {xmm0, xmm1}
    macro eq128 xmm1 = xmm1 / xmm2 {xmm0, xmm1}
    macro eq128 r1.dir = xmm1

    ; call ray scene intersection

    mov eax, r1
    mov ebx, hp

    """
    ASM += "call " + ray_scene_isect + """
    cmp eax, 0
    jne _maybe_visible
    ;no intersection ocure that mean that points are visible
    mov eax, 1 
    ret

    _maybe_visible:
    macro eq32 xmm0 = distance
    macro if xmm0 < hp.t goto accept 
    xor eax, eax 
    ret
    
    accept:
    mov eax, 1
    ret

    """

    assembler = util.get_asm()
    mc = assembler.assemble(ASM, True)
    #mc.print_machine_code()
    name = "visible" + str(util.unique())
    runtime.load(name, mc)
    


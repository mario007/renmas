import renmas
import renmas.core
import renmas.utils as util


# eax = pointer to ray structure
# ecx = pointer to minimum distance
# edx = pointer to hitpoint

# triangle paramters are on the on the stack
# esp - return address
# esp + 4 - address of v0
# esp + 8 - address of v1
# esp + 12 - address of v2
# esp + 16 - address of normal
# esp + 20 - mat_index
def intersect_ray_triangle_new(runtime, label, populate=True):
    asm_structs = util.structs("ray", "hitpoint")

    ASM = """ 
    #DATA
    float epsilon= 0.00001
    float one = 1.0
    """
    ASM += asm_structs + """
        ;eax = pointer to ray structure
        ;ecx = pointer to minimum distance
        ;edx = pointer to hitpoint
    #CODE
    ;macro eq128_128 xmm0 = ebx.triangle.p1 - ebx.triangle.p0, xmm1 = ebx.triangle.p2 - ebx.triangle.p0 
    """
    ASM += " global " + label + ":\n" 
    ASM += """
    mov ebp, dword [esp+4]
    movaps xmm0, oword [ebp]
    ;movaps xmm0, oword [ebx + triangle.p0]

    movaps xmm2, oword [eax + ray.dir]
    movaps xmm1, xmm0

    mov ebp, dword [esp+12]
    subps xmm1, oword [ebp]
    ;subps xmm1, oword [ebx + triangle.p2]

    movaps xmm3, xmm0
    subps xmm3, oword [eax + ray.origin]

    mov ebp, dword [esp+8]
    subps xmm0, oword [ebp]
    ;subps xmm0, oword [ebx + triangle.p1]

    
    ; f f h f
    movaps xmm4, xmm1
    movlhps xmm4, xmm3
    shufps xmm4, xmm4, 01110101B

    ; k k k l
    movaps xmm5, xmm2
    movhlps xmm5, xmm3
    shufps xmm5, xmm5, 00101010B 

    ; f f h f * k k k l
    movaps xmm7, xmm4
    mulps xmm7, xmm5

    ; g g g h
    movaps xmm6, xmm2
    movaps xmm4, xmm1
    movlhps xmm6, xmm3
    movhlps xmm4, xmm3
    shufps xmm6, xmm6, 11010101B
    shufps xmm4, xmm4, 10001010B

    ; j j l j

    ; g g g h * j j l j
    mulps xmm4, xmm6

    ; f f h f * k k k l - g g g h * j j l j
    subps xmm7, xmm4

    ; a d a a
    movaps xmm5, xmm0
    movlhps xmm5, xmm3
    shufps xmm5, xmm5, 00001000B

    ; a d a a * (f f h f * k k k l - g g g h * j j l j)
    mulps xmm7, xmm5

    ; i l i i
    movaps xmm5, xmm0
    movhlps xmm5, xmm3
    shufps xmm5, xmm5, 10100010B

    ; g g g h * i l i i
    mulps xmm6, xmm5

    ; e h e e
    movaps xmm4, xmm0
    movlhps xmm4, xmm3
    shufps xmm4, xmm4, 01011101B

    ; k k k l
    movaps xmm5, xmm2
    movhlps xmm5, xmm3
    shufps xmm5, xmm5, 00101010B 

    ; e h e e * k k k l
    mulps xmm5, xmm4

    ; g g g h * i l i i - e h e e * k k k l
    subps xmm6, xmm5

    ; b b d b
    movaps xmm5, xmm1
    movlhps xmm5, xmm3
    shufps xmm5, xmm5, 00100000B

    ; b b d b * (g g g h * i l i i - e h e e * k k k l)
    mulps xmm6, xmm5

    addps xmm7, xmm6

    ; j j l j
    movaps xmm5, xmm1
    movhlps xmm5, xmm3
    shufps xmm5, xmm5, 10001010B

    ; e e h e * j j l j 
    mulps xmm4, xmm5

    ; f f h f
    movaps xmm6, xmm1
    movlhps xmm6, xmm3
    shufps xmm6, xmm6, 01110101B

    ; i l i i
    movaps xmm5, xmm0
    movhlps xmm5, xmm3
    shufps xmm5, xmm5, 10100010B

    ; f f h f * i l i i
    mulps xmm6, xmm5

    ; e h e e * j j l j - f f h f * i l i i
    subps xmm4, xmm6

    ; c c c d
    movaps xmm5, xmm2
    movlhps xmm5, xmm3
    shufps xmm5, xmm5, 10000000B

    ; c c c d * (e h e e * j j l j - f f h f * i l i i)
    mulps xmm4, xmm5

    addps xmm7, xmm4
    macro broadcast xmm3 = xmm7[0]
    divps xmm7, xmm3

    movhlps xmm5, xmm7
    
    movaps xmm4, xmm7
    shufps xmm4, xmm4, 0x55 
    
    movaps xmm6, xmm7
    shufps xmm6, xmm6, 0xFF

    ; xmm7 = d
    ; xmm6 = td
    ; xmm5 = gamma
    ; xmm4 = beta

    pxor xmm3, xmm3
    macro if xmm4 < xmm3 goto _reject
    macro if xmm5 < xmm3 goto _reject
    addss xmm4, xmm5
    macro if xmm4 > one goto _reject

    comiss xmm6, dword [epsilon]
    jc _reject
    comiss xmm6, dword [ecx] ;minimum distance
    jnc _reject

    ;populate hitpoint structure
    ; t is in xmm6
    
    movaps xmm2, oword [eax + ray.dir]

    mov ebp, dword [esp + 16]
    movaps xmm3, oword [ebp]
    ;movaps xmm3, oword [ebx + triangle.normal]


    movss xmm4, dword [esp+20]
    ;movss xmm4, dword [ebx + triangle.mat_index]
    

    movss dword [edx + hitpoint.t], xmm6 
    movaps oword [edx + hitpoint.normal], xmm3
    movss dword [edx + hitpoint.mat_index], xmm4
    macro broadcast xmm5 = xmm6[0]
    mulps xmm5, xmm2

    macro eq128 edx.hitpoint.hit = xmm5 + eax.ray.origin

    mov eax, 1
    ret

    _reject:
    xor eax, eax
    ret
    """

    assembler = util.get_asm()
    mc = assembler.assemble(ASM, True)
    #mc.print_machine_code()
    name = "ray_triangle_isect" + str(util.unique())
    runtime.load(name, mc)

# eax = pointer to ray structure
# ecx = pointer to minimum distance
# edx = pointer to hitpoint

# triangle paramters are on the on the stack
# esp - return address
# esp + 4 - address of v0
# esp + 8 - address of v1
# esp + 12 - address of v2
# esp + 16 - address of normal
# esp + 20 - mat_index
def intersect_ray_triangle_avx(runtime, label, populate=True):
    asm_structs = util.structs("ray", "hitpoint")

    ASM = """ 
    #DATA
    float one = 1.0
    float zero = 0.0
    float epsilon = 0.00001
    float beta
    float coff 
    """
    ASM += asm_structs + """
        ;eax = pointer to ray structure
        ;ecx = pointer to minimum distance
        ;edx = pointer to hitpoint
    #CODE
    """
    ASM += " global " + label + ":\n" 
    ASM += """
    mov ebp, dword [esp+4]
    vmovaps xmm0, oword [ebp]
    ;vmovaps xmm0, oword [ebx + triangle.p0]


    vmovaps xmm2, oword [eax + ray.dir]

    mov ebp, dword [esp+12]
    vsubps xmm1, xmm0, oword [ebp]
    ;vsubps xmm1, xmm0, oword [ebx + triangle.p2]

    vsubps xmm3, xmm0, oword [eax + ray.origin]

    mov ebp, dword [esp+8]
    vsubps xmm0, xmm0, oword [ebp]
    ;vsubps xmm0, xmm0, oword [ebx + triangle.p1]

    vpermilps xmm0, xmm0, 11010010B ;rotate by 1
    vpermilps xmm2, xmm2, 11001001B ; rotate by 2
    
    vblendps xmm4, xmm0, xmm1, 0010b
    vblendps xmm4, xmm4, xmm2, 1
   
    vblendps xmm5, xmm0, xmm1, 0100b
    vblendps xmm5, xmm5, xmm2, 0010b

    vpermilps xmm6, xmm4, 11010010B
    vpermilps xmm7, xmm5, 11001001B

    vmulps xmm4, xmm4, xmm5
    vmulps xmm6, xmm6, xmm7
    vblendps xmm5, xmm0, xmm1, 0001B
    vblendps xmm5, xmm5, xmm2, 0100B
    vsubps xmm4, xmm4, xmm6
    vdpps xmm7, xmm4, xmm5, 0xf1

    vpermilps xmm3, xmm3, 11010010B ;rotate by 1
    vblendps xmm4, xmm1, xmm2, 0001B
    vmovss xmm6, dword [one]
    vblendps xmm4, xmm4, xmm3, 0100B
    vblendps xmm5, xmm1, xmm2, 0010B
    vdivss xmm6, xmm6, xmm7

    vblendps xmm5, xmm5, xmm3, 0001B

    vpermilps xmm7, xmm5, 11001001B
    vmovss dword [coff], xmm6
    vpermilps xmm6, xmm4, 11010010B

    vmulps xmm4, xmm4, xmm5
    vmulps xmm6, xmm6, xmm7

    vblendps xmm5, xmm1, xmm2, 0100B
    vblendps xmm5, xmm5, xmm3, 0010B

    vsubps xmm4, xmm4, xmm6
    vdpps xmm7, xmm4, xmm5, 0xf1

    vmulss xmm7, xmm7, dword [coff]
    vcomiss xmm7, dword [zero]
    jc _reject ;beta less then zero reject 
    vmovss dword [beta], xmm7
    
    vpermilps xmm3, xmm3, 11001001B ; rotate by 2

    vblendps xmm4, xmm0, xmm2, 0001B
    vblendps xmm4, xmm4, xmm3, 0010B
    vpermilps xmm6, xmm4, 11010010B
    vblendps xmm5, xmm0, xmm2, 0010B
    vblendps xmm5, xmm5, xmm3, 0100B
    vpermilps xmm7, xmm5, 11001001B
    vmulps xmm4, xmm4, xmm5
    vmulps xmm6, xmm6, xmm7
    vblendps xmm5, xmm0, xmm2, 0100B
    vblendps xmm5, xmm5, xmm3, 0001B
    vsubps xmm4, xmm4, xmm6
    vdpps xmm7, xmm4, xmm5, 0xf1

    vmulss xmm7, xmm7, dword [coff]
    vcomiss xmm7, dword [zero]
    jc _reject ;beta less then zero reject 
    vaddss xmm7, xmm7, dword [beta]
    vcomiss xmm7, dword [one]
    jnc _reject

    vpermilps xmm3, xmm3, 11001001B ; rotate by 2

    vblendps xmm4, xmm0, xmm1, 0010B
    vblendps xmm4, xmm4, xmm3, 0001B
    vpermilps xmm6, xmm4, 11010010B
    vblendps xmm5, xmm0, xmm1, 0100B
    vblendps xmm5, xmm5, xmm3, 0010B
    vpermilps xmm7, xmm5, 11001001B
    vmulps xmm4, xmm4, xmm5
    vmulps xmm6, xmm6, xmm7
    vblendps xmm5, xmm0, xmm1, 0001B
    vblendps xmm5, xmm5, xmm3, 0100B
    vsubps xmm4, xmm4, xmm6
    vdpps xmm7, xmm4, xmm5, 0xf1
    vmulss xmm7, xmm7, dword [coff]
    vcomiss xmm7, dword [epsilon]
    jc _reject
    vcomiss xmm7, dword [ecx] ;minimum distance
    jnc _reject


    ;populate hitpoint structure
    ; t is in xmm7
    vmovss dword [edx + hitpoint.t], xmm7 
    macro broadcast xmm6 = xmm7[0]
    ;macro eq128_32 edx.hitpoint.normal = ebx.triangle.normal, edx.hitpoint.mat_index = ebx.triangle.mat_index

    ;vpermilps xmm2, xmm2, 11001001B ; rotate by 2
    macro eq128 xmm2 = eax.ray.dir
    vmulps xmm6, xmm6, xmm2
    macro eq128 edx.hitpoint.hit = xmm6 + eax.ray.origin

    mov ebp, dword [esp + 16]
    vmovaps xmm0, oword [ebp]
    vmovss xmm1, dword [esp + 20]
    macro eq128 edx.hitpoint.normal = xmm0
    macro eq32 edx.hitpoint.mat_index = xmm1

    mov eax, 1
    ret

    _reject:
    mov eax, 0
    ret
"""


    assembler = util.get_asm()
    mc = assembler.assemble(ASM, True)
    #mc.print_machine_code()
    name = "ray_triangle_isect" + str(util.unique())
    runtime.load(name, mc)

# eax = pointer to ray structure
# ecx = pointer to minimum distance
# edx = pointer to hitpoint

# triangle paramters are on the on the stack
# esp - return address
# esp + 4 - address of v0
# esp + 8 - address of v1
# esp + 12 - address of v2
# esp + 16 - address of normal
# esp + 20 - mat_index

def intersect_ray_triangle(runtime, label, populate=True):
    asm_structs = util.structs("ray", "hitpoint")

    ASM = """ 
    #DATA
    float epsilon = 0.00001
    float neg_epsilon = -0.00001
    float one = 1.0
    float zero = 0.0
    uint32 mask_abs[4] = 0x7FFFFFFF, 0, 0, 0
    float minus_one = -1.0
    """
    ASM += asm_structs + """
        ;eax = pointer to ray structure
        ;ecx = pointer to minimum distance
        ;edx = pointer to hitpoint
    #CODE
    ;macro eq128_128 xmm0 = ebx.triangle.p1 - ebx.triangle.p0, xmm1 = ebx.triangle.p2 - ebx.triangle.p0 
    """
    ASM += " global " + label + ":\n" 
    if util.AVX:
        ASM += """
        mov ebp, dword [esp + 8]
        vmovaps xmm0, oword [ebp]
        mov ebp, dword [esp+4]
        vsubps xmm0, xmm0, oword [ebp]
        mov ebp, dword [esp + 12]
        vmovaps xmm1, oword [ebp]
        mov ebp, dword [esp+4]
        vsubps xmm1, xmm1, oword [ebp]
        """
    else:
        ASM += """
        mov ebp, dword [esp + 8]
        movaps xmm0, oword [ebp]
        mov ebp, dword [esp+4]
        subps xmm0, oword [ebp]
        mov ebp, dword [esp + 12]
        movaps xmm1, oword [ebp]
        mov ebp, dword [esp+4]
        subps xmm1, oword [ebp]
        """

    ASM += """
    ; e1 = xmm0 , e2 = xmm1
    macro eq128_128 xmm2 = eax.ray.dir, xmm3 = xmm1 {xmm0, xmm1}

    ; p = d x e2
    macro eq128_128 xmm4 = xmm2, xmm5 = xmm3 {xmm0, xmm1}
    """

    if util.AVX:
        ASM += """
            vshufps xmm2, xmm2, xmm2, 0xC9
            vshufps xmm3, xmm3, xmm3, 0xD2
            macro eq128 xmm2 = xmm2 * xmm3 {xmm0, xmm1}
            vshufps xmm4, xmm4, xmm4, 0xD2
            vshufps xmm5, xmm5, xmm5, 0xC9
        """
    else:
        ASM += """
            shufps xmm2, xmm2, 0xC9
            shufps xmm3, xmm3, 0xD2
            macro eq128 xmm2 = xmm2 * xmm3 {xmm0, xmm1}
            shufps xmm4, xmm4, 0xD2
            shufps xmm5, xmm5, 0xC9
        """
    ASM += """
        macro eq128 xmm4 = xmm4 * xmm5 {xmm0, xmm1, xmm2}
        macro eq128 xmm2 = xmm2 - xmm4 {xmm0, xmm1}

        macro dot xmm3 = xmm0 * xmm2 {xmm0, xmm1}
    """
    if util.AVX:
        ASM += "vpabsd xmm4, xmm3 \n"
    else:
        ASM += "movaps xmm4, oword [mask_abs] \n"
        ASM += "andps xmm4, xmm3 \n"

    ASM += """

        macro if xmm4 < epsilon goto reject
        macro eq32 xmm4 = one / xmm3 {xmm0, xmm1, xmm2, xmm3}

        ; f = xmm4
        ;macro eq128 xmm5 = eax.ray.origin - ebx.triangle.p0 {xmm0, xmm1, xmm2, xmm3, xmm4}
    """
    if util.AVX:
        ASM += """
        mov ebp, dword [esp+4]
        macro eq128 xmm5 = eax.ray.origin
        vsubps xmm5, xmm5, oword [ebp]
        """
    else:
        ASM += """
        mov ebp, dword [esp+4]
        macro eq128 xmm5 = eax.ray.origin
        subps xmm5, oword [ebp]
        """
    ASM += """
        ; s = xmm5

        macro dot xmm2 = xmm2 * xmm5 {xmm0, xmm1, xmm3, xmm4}
        ;s * p(s dot p) = xmm2
        macro eq32 xmm6 = xmm4 * xmm2 {xmm0, xmm1, xmm2, xmm3, xmm4, xmm5}

        macro if xmm6 < zero goto reject
        macro if xmm6 > one goto reject

        ; q = s x e1 
        macro eq128_128 xmm3 = xmm5, xmm7 = xmm0 
    """
    if util.AVX:
        ASM += """
            vshufps xmm5, xmm5, xmm5, 0xC9
            vshufps xmm0, xmm0, xmm0, 0xD2
            macro eq128 xmm0 = xmm0 * xmm5 

            vshufps xmm3, xmm3, xmm3, 0xD2
            vshufps xmm7, xmm7, xmm7, 0xC9
        """
    else:
        ASM += """
            shufps xmm5, xmm5, 0xC9
            shufps xmm0, xmm0, 0xD2
            macro eq128 xmm0 = xmm0 * xmm5 

            shufps xmm3, xmm3, 0xD2
            shufps xmm7, xmm7, 0xC9
        """

    ASM += """
        macro eq128 xmm3 = xmm3 * xmm7 
        macro eq128 xmm0 = xmm0 - xmm3

        macro dot xmm7 = xmm0 * eax.ray.dir {xmm1}
        macro eq32 xmm7 = xmm7 * xmm4

        macro if xmm7 < zero goto reject
        macro eq32 xmm7 = xmm7 + xmm6
        macro if xmm7 > one goto reject

        macro dot xmm6 = xmm1 * xmm0
        macro eq32 xmm6 = xmm6 * xmm4

        ;populate hitpoint structure
        ; t is in xmm6 , t can be negative so we eleminate those
        macro if xmm6 < zero goto reject
        macro if xmm6 > ecx goto reject
    """
    if populate:
        ASM += """
        macro eq32 edx.hitpoint.t = xmm6
        macro broadcast xmm7 = xmm6[0]
        ;macro eq128_32 edx.hitpoint.normal = ebx.triangle.normal, edx.hitpoint.mat_index = ebx.triangle.mat_index
        """
        if util.AVX:
            ASM += """
            mov ebp, dword [esp + 16]
            vmovaps xmm0, oword [ebp]
            vmovss xmm1, dword [esp + 20]
            """
        else:
            ASM += """
            mov ebp, dword [esp + 16]
            movaps xmm0, oword [ebp]
            movss xmm1, dword [esp + 20]
            """
        ASM += """
        macro eq128 edx.hitpoint.normal = xmm0
        macro eq32 edx.hitpoint.mat_index = xmm1
        macro eq128 xmm5 = xmm7 * eax.ray.dir
        macro eq128 edx.hitpoint.hit = xmm5 + eax.ray.origin
        """
    ASM += """

        mov eax, 1
        ret

        reject:
        mov eax, 0 
        ret


    """
    assembler = util.get_asm()
    mc = assembler.assemble(ASM, True)
    #mc.print_machine_code()
    name = "ray_triangle_isect" + str(util.unique())
    runtime.load(name, mc)


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

def multiple_isect_asm(runtime, label):

    asm_structs = util.structs("ray", "hitpoint")

    ASM = """
    #DATA
    """
    ASM += asm_structs + """
    float min_dist = 999999.0
    float max_dist = 999999.0
    float zero = 0.0
    float one = 1.0
    float epsilon = 0.00001

    #CODE
    """
    ASM += " global " + label + ":\n" + """
    ; eax - ray,  ebx - hp, ecx - min_dist, esi - ptr_arr, edi - nobj
    ; 64-bit version will bi i little different beacuse of different size of array
    macro eq32 min_dist = max_dist + one
    mov ecx, min_dist
    push ecx
    push eax
    push ebx
    push esi
    push edi
    mov edx, dword [zero]
    mov dword [ebx + hitpoint.t], edx


    _objects_loop:
    mov eax, dword [esp + 12] ; address of ray
    mov ecx, dword [esp + 16] ; address of minimum distance
    mov edx, dword [esp + 8]  ; address of hitpoint
    mov esi, dword [esp + 4] ; array of objects and functions obj_ptr:func_ptr
    mov ebx, dword [esi]  ; put in ebx address of object
    call dword [esi + 4]  ; function pointer
    cmp eax, 0  ; 0 - no intersection ocur 1 - intersection ocur
    jne _update_distance
    _next_object:
    sub dword [esp], 1  
    jz _end_objects
    add dword [esp + 4], 8  ;increment array by 8
    jmp _objects_loop


    _update_distance:
    mov eax, dword [esp + 8]
    mov ebx, dword [eax + hitpoint.t]

    mov edx, dword [esp + 16] ;populate new minimum distance
    mov dword [edx], ebx
    jmp _next_object
    
    _end_objects:
    add esp, 20 
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

    asm = util.get_asm()
    mc = asm.assemble(ASM, True)
    #mc.print_machine_code()
    name = "ray_objects_intersection" + str(util.unique())
    runtime.load(name, mc)


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
    float epsilon = 0.00001
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


geometry = renmas.geometry
def lst_shapes():
    return geometry.isect_shapes()

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
    


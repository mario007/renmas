
import renmas
import renmas.interface as ren 

asm_structs = renmas.utils.structs("sample", "ray", "hitpoint")
ASM = """
#DATA
"""
ASM += asm_structs + """
    sample sam
    ray r1
    hitpoint hp
    hitpoint background
    uint32 end_sam
    float back[4] = 0.00, 0.00, 0.00, 0.00
    float minus_one[4] = -1.0, -1.0, -1.0, 0.0
    float one[4] = 1.0, 1.0, 1.0, 1.0
    float zero[4] = 0.0, 0.0, 0.0, 0.0

    float transmitance = 1.0
    uint32 max_depth = 4
    uint32 cur_depth = 0
    float Ld[40] ;this is for maxdepth of 10
    float Lr[40]
    float epsilon = 0.02

#CODE
    macro eq128 background.spectrum = back

    _next_sample:
    macro eq32 transmitance = one

    ; put pointer to sample structre in eax and generate sample
    mov eax, sam
    call get_sample
    ; test to si if we are done sampling picture 
    cmp eax, 0
    je _end_sampling
    
    ; now we must calculate ray
    mov eax, r1
    mov ebx, sam 
    call generate_ray

    ; now intersect ray with shapes
    ; eax = pointer_to_ray, ebx = pointer_to_hitpoint
    mov eax, r1
    mov ebx, hp
    call scene_isect 

    ;if ray hit some object we must calculate shading
    ; in eax is result of intersection routine
    cmp eax, 0
    je _background


    ; call shading routine
    mov eax, hp
    mov ebx, r1
    macro eq128 eax.hitpoint.wo = ebx.ray.dir * minus_one 
    call shade
    mov eax, r1
    mov ebx, hp
    macro eq128 eax.ray.origin = ebx.hitpoint.hit 
    macro eq128 eax.ray.dir = ebx.hitpoint.wi

    macro eq32 xmm1 = ebx.hitpoint.ndotwi 
    macro eq32 xmm0 = ebx.hitpoint.pdf
    macro eq32 xmm1 = xmm1 / xmm0
    macro broadcast xmm1 = xmm1[0]
    macro eq128 xmm1 = xmm1 * ebx.hitpoint.brdf
    macro eq128 xmm0 = ebx.hitpoint.spectrum
    macro eq128 Lr = xmm1
    macro eq128 Ld = xmm0
    macro dot xmm2 = xmm1 * xmm1
    macro eq32 transmitance = xmm2
    mov dword [cur_depth], 1

    macro eq128 xmm3 = one
    macro dot xmm3 = xmm3 * ebx.hitpoint.le 
    macro if xmm3 > epsilon goto emiter_hit

    _path_construct:
    mov eax, dword [cur_depth]
    cmp eax, dword [max_depth]
    je __end_path
    macro eq32 xmm0 = transmitance
    macro if xmm0 < epsilon goto __end_path
    mov eax, r1
    mov ebx, hp
    call scene_isect 
    cmp eax, 0
    je __end_path
    mov eax, hp
    mov ebx, r1
    macro eq128 eax.hitpoint.wo = ebx.ray.dir * minus_one 
    call shade
    mov ebx, hp
    macro eq128 xmm3 = one
    macro dot xmm3 = xmm3 * ebx.hitpoint.le 
    macro if xmm3 > epsilon goto __end_path_light
    mov eax, r1
    macro eq128 eax.ray.origin = ebx.hitpoint.hit 
    macro eq128 eax.ray.dir = ebx.hitpoint.wi
    macro eq32 xmm1 = ebx.hitpoint.ndotwi 
    macro eq32 xmm0 = ebx.hitpoint.pdf
    macro eq32 xmm1 = xmm1 / xmm0
    macro broadcast xmm1 = xmm1[0]
    macro eq128 xmm1 = xmm1 * ebx.hitpoint.brdf
    macro eq128 xmm0 = ebx.hitpoint.spectrum
    mov edx, dword [cur_depth]
    imul edx, edx, 16
    movaps oword [Lr + edx], xmm1
    movaps oword [Ld + edx], xmm0
    macro dot xmm2 = xmm1 * xmm1
    macro eq32 transmitance = xmm2
    add dword [cur_depth], 1

    jmp _path_construct

    __end_path_light:
    ;macro eq128 xmm0 = ebx.hitpoint.le
    macro eq128 xmm0 = zero
    jmp _end_p

    __end_path:
    macro eq128 xmm0 = zero 

    _end_p:
    mov edx, dword [cur_depth]
    sub edx, 1
    imul edx, edx, 16
    movaps xmm2, oword [Lr + edx]
    movaps xmm3, oword [Ld + edx]
    macro eq128 xmm0 = xmm0 * xmm2
    macro eq128 xmm0 = xmm0 + xmm3

    sub dword [cur_depth], 1
    jnz _end_p

    mov eax, hp
    macro eq128 eax.hitpoint.spectrum = xmm0
    mov ebx, sam 
    call add_sample
    mov dword [cur_depth], 0
    jmp _next_sample
    

    emiter_hit:
    macro eq128 ebx.hitpoint.spectrum = ebx.hitpoint.le
    mov eax, ebx
    mov ebx, sam
    call add_sample
    mov dword [cur_depth], 0
    jmp _next_sample


    _background: ; add background sample to film
    mov eax, background
    mov ebx, sam
    call add_sample

    jmp _next_sample

    
    _end_sampling:
    mov dword [end_sam], 0
#END
"""

def prepare_pathtracer_asm(runtime):
    asm = renmas.utils.get_asm()
    mc = asm.assemble(ASM)
    ds = runtime.load("pathtracer", mc)



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

#CODE
    macro eq128 background.spectrum = back

    _next_sample:
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
    ; add_sample to film
    mov eax, hp
    mov ebx, sam 
    call add_sample
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

def prepare_raycast_asm(runtime):
    asm = renmas.utils.get_asm()
    mc = asm.assemble(ASM)
    ds = runtime.load("raycast", mc)


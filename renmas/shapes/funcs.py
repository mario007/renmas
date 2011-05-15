
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


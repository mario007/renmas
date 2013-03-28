

def sample_hemisphere_asm(label, AVX=False, BIT64=True):
    rnd_label = 'random_ypu6man0xj'
    sincos_label = 'sincos_qpyaa9akyj'

    code = """ 
    #DATA

    float pu[4]
    float pv[4]
    float pw[4]
    float one[4] = 1.0, 1.0, 1.0, 1.0
    float two[4] = 2.0, 2.0, 2.0, 2.0
    float pi[4] = 3.14159265359, 3.14159265359, 3.14159265359, 3.14159265359
    float sample[4]
    uint32 idx = 0
    #CODE
    """
    code += 'global ' + label + ':\n' + """
    
    sub dword [idx], 1
    js _calculate_samples
    _return_sample:
    mov ebx, dword [idx]
    """
    if BIT64:
        code += """
        mov rcx, pu
        mov edx, dword [rcx + 4*rbx]
        mov rcx, pv
        mov esi, dword [rcx + 4*rbx]
        mov rcx, pw
        mov edi, dword [rcx + 4*rbx]
        """
    else:
        code += """
        mov ecx, pu
        mov edx, dword [ecx + 4*ebx]
        mov ecx, pv
        mov esi, dword [ecx + 4*ebx]
        mov ecx, pw
        mov edi, dword [ecx + 4*ebx]
        """
    code += """
    mov dword [sample], edx
    mov dword [sample + 4], esi
    mov dword [sample + 8], edi
    macro eq128 xmm0 = sample {xmm7}
    ret

    _calculate_samples:
    """
    code += 'call ' + rnd_label + '\n' + """
    macro eq128 xmm1 = one - xmm0

    """
    if AVX:
        code += "vsqrtps xmm0, xmm0 \n"
        code += "vsqrtps xmm1, xmm1 \n"
    else:
        code += "sqrtps xmm0, xmm0 \n"
        code += "sqrtps xmm1, xmm1 \n"

    code += """

    macro eq128 pw = xmm0 {xmm0}
    macro eq128 pu = xmm1 {xmm0}
    macro eq128 pv = xmm1 {xmm0}
    """
    code += 'call ' + rnd_label + '\n' + """
    macro eq128 xmm0 = xmm0 * pi * two
    """
    code += 'call ' + sincos_label + '\n' + """
    macro eq128 xmm6 = xmm6 * pu
    macro eq128 xmm0 = xmm0 * pv

    macro eq128 pu = xmm6  {xmm6}
    macro eq128 pv = xmm0  {xmm0}
    mov dword [idx], 3
    jmp _return_sample

    """
    
    funcs = [('random', rnd_label), ('sincos_ps', sincos_label)]
    return (code, funcs)


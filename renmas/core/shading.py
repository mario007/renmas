import renmas

def shade(hp):
    #loop through lights
    lights = renmas.interface.lst_lights()
    tmp_spec = renmas.core.Spectrum(0.0, 0.0, 0.0)
    for light in lights:
        if light.L(hp) is True: #light is visible
            renmas.interface.get_material(hp.material).brdf(hp)
            tmp_spec = tmp_spec + hp.spectrum
    hp.spectrum = tmp_spec
    return hp

def generate_shade(runtime, label,  visible_label):
    materials = renmas.interface.lst_materials()
    lights = renmas.interface.lst_lights()

    nmaterials = len(materials)
    nlights = len(lights)

    asm_structs = renmas.utils.structs("hitpoint")
    #loop through list of lights and do shading
    #TODO later implement smarter shade where we on random pick just light??? study this aproach
    #eax is pointer to hitpoint
    ASM = """
        #DATA
    """
    ASM += asm_structs
    ASM += "uint32 lights_ptrs[" + str(nlights) + "]\n"
    ASM += "uint32 materials_ptrs[" + str(nmaterials) + "]\n"
    ASM += "uint32 nlights \n"
    ASM += "uint32 cur_light \n"
    ASM += """
        float zero_spectrum[4] = 0.0, 0.0, 0.0, 0.0
        float curr_spectrum[4]

        uint32 hp_ptr 

        #CODE
    """
    ASM += "global " + label + ":\n" + """
        macro eq128 curr_spectrum = zero_spectrum
        mov dword [cur_light], 0 
        mov dword [hp_ptr], eax

        next_light:
        ; check if include all lights and finish shading if we are  
        mov ebx, dword [cur_light]
        cmp ebx, dword [nlights]
        je _end_shading

        ; call shading for current light
        mov eax, dword [hp_ptr]
        call dword [lights_ptrs + ebx*4]
        add dword [cur_light], 1 ;move to next light in next iteration
        
        ; check to see if we must call brdf of material
        mov eax, dword [hp_ptr]
        mov edx, dword [eax + hitpoint.visible]
        cmp edx, 0
        je next_light
        
        ; call brdf of material
        mov eax, dword [hp_ptr]
        mov ebx, dword [eax + hitpoint.mat_index]
        call dword [materials_ptrs + 4*ebx] 
        mov eax, dword [hp_ptr]
        macro eq128 curr_spectrum = curr_spectrum + eax.hitpoint.spectrum
        jmp next_light

        _end_shading:
        mov eax, dword [hp_ptr]
        macro eq128 eax.hitpoint.spectrum = curr_spectrum
        ret

    """

    l_ptrs = []
    for l in lights:
        l.L_asm(runtime, visible_label)
        l_ptrs.append(l.func_ptr)
    l_ptrs = tuple(l_ptrs)
    m_ptrs = []
    for m in materials:
        m.brdf_asm(runtime)
        m_ptrs.append(m.func_ptr)
    m_ptrs = tuple(m_ptrs)

    asm = renmas.utils.get_asm()
    mc = asm.assemble(ASM, True) 
    name = "shade" + str(renmas.utils.unique())
    ds = runtime.load(name, mc)
    ds["lights_ptrs"] = l_ptrs
    ds["materials_ptrs"] = m_ptrs
    ds["nlights"] = nlights


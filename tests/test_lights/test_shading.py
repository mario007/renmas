
import renmas
import renmas.core
import renmas.samplers
import renmas.camera
import renmas.maths
import renmas.gui
import renmas.lights
import renmas.interface as ren 
import renmas.utils as util

from tdasm import Runtime

def build_scene():
    ren.create_lambertian("m1", 0.7, 0.6, 0.7)
    idx = ren.get_mat_idx("m1")
    ren.create_sphere(0, 0, 0, 1, idx)
    
    ren.create_point_light("p1", (10.0, 5.0, 8.0), (1.0, 1.0, 1.0))
    #ren.create_point_light("p2", (3.0, 1.0, 1.0), (1.0, 1.0, 1.0))

def visible(runtime):
    dyn_arrays = ren.dyn_arrays()
    renmas.shapes.linear_isect_asm(runtime, "scene_isect", dyn_arrays)
    renmas.shapes.visible_asm(runtime, "visible", "scene_isect")

runtime = Runtime()
build_scene()
visible(runtime)

def create_hitpoint():
    hitpoint = renmas.shapes.HitPoint()
    hitpoint.hit_point = renmas.maths.Vector3(1.0, 0.0, 0.0)
    hitpoint.normal = renmas.maths.Vector3(2.2, -4.3, 4.4)
    hitpoint.normal.normalize()
    hitpoint.material = 0
    return hitpoint

def shade(hp):
    #loop through lights
    lights = ren.lst_lights()
    tmp_spec = renmas.core.Spectrum(0.0, 0.0, 0.0)
    for light in lights:
        if light.L(hp) is True: #light is visible
            ren.get_material(hp.material).brdf(hp)
            tmp_spec = tmp_spec + hp.spectrum
    hp.spectrum = tmp_spec
    return hp

def generate_shade(runtime, label,  visible_label):
    materials = ren.lst_materials()
    lights = ren.lst_lights()

    nmaterials = len(materials)
    nlights = len(lights)

    asm_structs = util.structs("hitpoint")
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

    asm = util.get_asm()
    mc = asm.assemble(ASM, True) 
    name = "shade" + str(util.unique())
    ds = runtime.load(name, mc)
    ds["lights_ptrs"] = l_ptrs
    ds["materials_ptrs"] = m_ptrs
    ds["nlights"] = nlights


generate_shade(runtime, "shade", "visible")

asm_structs = renmas.utils.structs("hitpoint")
ASM = """
    #DATA
"""
ASM += asm_structs + """
    hitpoint hp1

    #CODE
    mov eax, hp1
    call shade 

    #END
"""

asm = util.get_asm()
mc = asm.assemble(ASM) 
ds = runtime.load("test", mc)

hitpoint = create_hitpoint()
v = hitpoint.hit_point
ds["hp1.hit"] = (v.x, v.y, v.z, 0.0)
v = hitpoint.normal
ds["hp1.normal"] = (v.x, v.y, v.z, 0.0)
ds["hp1.mat_index"] = hitpoint.material


runtime.run("test")
print("ASM results")
print("wi = ", ds["hp1.wi"])
print("ndotwi =", ds["hp1.ndotwi"])
print("spectrum =", ds["hp1.spectrum"])
print("visible", ds["hp1.visible"])

shade(hitpoint)
print("Python")
print("visible =", hitpoint.visible)
print("spectrum =", hitpoint.spectrum)
print("wi =", hitpoint.wi)
print("ndotwi =", hitpoint.ndotwi)




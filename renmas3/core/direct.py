import platform
from .shade_point import ShadePoint

class DirectLighting:
    def __init__(self, renderer):
        self._renderer = renderer

    def estimate_direct(self, sp):

        #TODO make option - one light or all light strategy
        lights = self._renderer.lights_mgr.lights
        material = self._renderer.material_mgr._materials_idx[sp.material]

        tmp_spec = self._renderer.color_mgr.zero_spectrum()
        for light in lights:
            light.L(sp)
            vis = self._renderer.shape_mgr.visibility(sp.light_position, sp.hit)
            if vis: #light is visible
                material.brdf(sp)
                tmp_spec += sp.f_spectrum * sp.light_spectrum 
        return tmp_spec

    #eax - pointer to shadepoint 
    #eax - pointer to returned spectrum
    def estimate_direct_asm(self, runtimes, label):
        bits = platform.architecture()[0]
        vis_label = 'visible' + str(id(self))
        self._renderer.shape_mgr.visibility_asm(runtimes, vis_label)

        lights = self._renderer.lights_mgr.lights
        spec_struct = self._renderer.color_mgr.zero_spectrum().struct()
        code = '#DATA \n' + spec_struct + ShadePoint.struct()
        if bits == '64bit':
            code += "uint64 materials_ptrs[" + str(len(self._renderer.material_mgr.materials)) + "]\n"
            code += "uint64 hp_ptr\n"
        else:
            code += "uint32 materials_ptrs[" + str(len(self._renderer.material_mgr.materials)) + "]\n"
            code += "uint32 hp_ptr\n"
        code += """
            float zero = 0.0
            spectrum temp_spectrum
            #CODE
        """
        code += "global " + label + ":\n"
        if bits == '64bit':
            code += "mov qword [hp_ptr], rax\n"
        else:
            code += "mov dword [hp_ptr], eax\n"
        code += """
        macro mov eax, temp_spectrum
        macro call zero xmm0
        macro spectrum eax = xmm0
        """
        for light in lights:
            light.L_asm(runtimes, self._renderer.assembler)
            if bits == '64bit':
                code += 'mov rax, qword [hp_ptr]\n'
                code += 'call ' + light.L_asm_label + '\n'
                code += 'mov rax, qword [hp_ptr]\n'
            else:
                code += 'mov eax, dword [hp_ptr]\n'
                code += 'call ' + light.L_asm_label + '\n'
                code += 'mov eax, dword [hp_ptr]\n'
            code += 'macro eq128 xmm0 = eax.shadepoint.light_position\n'
            code += 'macro eq128 xmm1 = eax.shadepoint.hit\n'
            code += 'call ' + vis_label + '\n'
            #TODO --- separate this section of code in separate function
            code += """
                cmp eax, 1
                jne _next_light
                ; call brdf of material
                """
            if bits == '64bit':
                code += """
                mov rax, qword [hp_ptr]
                mov ebx, dword [rax + shadepoint.material]
                mov rcx, materials_ptrs
                call qword [rcx + 4*rbx] 
                mov rax, qword [hp_ptr]
                """
            else:
                code += """
                mov eax, dword [hp_ptr]
                mov ebx, dword [eax + shadepoint.material]
                call dword [materials_ptrs + 4*ebx] 
                mov eax, dword [hp_ptr]
                """
            code += """
                macro lea ebx, dword [eax + shadepoint.f_spectrum]
                macro lea ecx, dword [eax + shadepoint.light_spectrum]
                macro spectrum ecx = ecx * ebx 
                """
            if bits == '64bit':
                code += "mov rax, qword [hp_ptr]\n"
            else:
                code += "mov eax, dword [hp_ptr]\n"

            code += """
                macro lea ecx, dword [eax + shadepoint.light_spectrum]
                macro mov edx, temp_spectrum 
                macro spectrum edx = edx + ecx

                _next_light:
                """
        code += """
            macro mov eax, temp_spectrum 
            ret
        """

        ren = self._renderer
        for m in self._renderer.material_mgr.materials:
            m.brdf_asm(runtimes, ren.assembler)

        #print (code)
        mc = ren.assembler.assemble(code, True) 
        name = "estimate_direct" + str(id(self))
        for r in runtimes:
            ds = r.load(name, mc)
            m_ptrs = [r.address_module(m.brdf_asm_name) for m in self._renderer.material_mgr.materials]
            ds["materials_ptrs"] = tuple(m_ptrs)



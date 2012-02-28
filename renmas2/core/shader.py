
from ..lights import Light
from .material import Material
from .spectrum import Spectrum

class Shader:
    def __init__(self, renderer):
        self._renderer = renderer

        # containers for materials
        self._materials = {}
        self._materials_lst = []
        self._materials_idx = {}

        # containers for lights  
        self._lights = {}
        self._lights_lst = []

    def mat_idx(self, name):
        if name in self._materials:
            return self._materials[name][1]
        return None
    
    def material_name(self, idx):
        material = self._materials_idx[idx]
        for key, value in self._materials.items():
            if value[0] == material:
                return key
        return None

    def material(self, name):
        if name in self._materials:
            return self._materials[name][0]
        return None
   
    def material_names(self):
        return self._materials.keys()

    def light_names(self):
        return self._lights.keys()

    def light(self, name):
        if name in self._lights:
            return self._lights[name]
        return None

    def convert_spectrums(self):
        for l in self._lights_lst:
            l.convert_spectrums(self._renderer.converter)
        for m in self._materials_lst:
            m.convert_spectrums(self._renderer.converter)

    def add(self, name, obj): #material or light
        if isinstance(obj, Material): #TODO check if material allready exist
            if name in self._materials:
                return #Material allread exist -- put information in log
            self._materials[name] = (obj, len(self._materials_lst)) 
            self._materials_idx[len(self._materials_lst)] = obj
            self._materials_lst.append(obj)
        elif isinstance(obj, Light):
            if name in self._lights:
                return #Light allready exist -- create log
            self._lights[name] = obj
            self._lights_lst.append(obj)

    def shade(self, hp):

        # direct illumination
        #loop through lights ALL lights strategy !!!TODO make option - one light or all light strategy
        lights = self._lights_lst
        material = self._materials_idx[hp.material]

        # emisive material - TODO - later
        #hp.le = material.Le(hp)
        
        tmp_spec = self._renderer.converter.zero_spectrum()
        for light in lights:
            if light.L(hp, self._renderer): #light is visible
                material.f(hp)
                tmp_spec += hp.f_spectrum.mix_spectrum(hp.l_spectrum) * hp.ndotwi 

        # indirect illumination
        #to calculate next direction
        # first calculate next direction i pdf - next direction is in wi
        #material.next_direction(hp)
        return tmp_spec

    #eax - pointer to hitpoint
    def shade_asm(self, runtimes, label, visible_label):

        code = """
            #DATA
        """
        code += self._renderer.structures.structs(('hitpoint',)) + """
        """
        code += "uint32 lights_ptrs[" + str(len(self._lights_lst)+1) + "]\n"
        code += "uint32 materials_ptrs[" + str(len(self._materials_lst)) + "]\n"
        code += "uint32 samplings[" + str(len(self._materials_lst)) + "]\n"
        code += "uint32 le_ptrs[" + str(len(self._materials_lst)) + "]\n"
        code += "uint32 nlights \n"
        code += "uint32 cur_light \n"
        code += """
            uint32 hp_ptr 
            float zero = 0.0
            spectrum temp_spectrum
            #CODE
        """
        code += "global " + label + ":\n" + """
            mov dword [hp_ptr], eax
            mov dword [cur_light], 0 
            mov eax, temp_spectrum
            macro call zero xmm0
            macro spectrum eax = xmm0

            ;light emmision --- later

            next_light:
            mov ebx, dword [cur_light]
            cmp ebx, dword [nlights]
            je _end_shading

            ; call shading for current light
            mov eax, dword [hp_ptr]
            call dword [lights_ptrs + ebx*4]
            add dword [cur_light], 1 ;move to next light

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
            lea ebx, dword [eax + hitpoint.f_spectrum]
            lea ecx, dword [eax + hitpoint.l_spectrum]
            macro spectrum ecx = ecx * ebx 
            mov eax, dword [hp_ptr]
            macro eq32 xmm0 = eax.hitpoint.ndotwi
            lea ecx, dword [eax + hitpoint.l_spectrum]
            macro spectrum ecx = xmm0 * ecx 
            mov edx, temp_spectrum 
            macro spectrum edx = edx + ecx
            jmp next_light

            _end_shading:
            mov eax, temp_spectrum
            mov ebx, dword [hp_ptr]
            lea ecx, dword [ebx + hitpoint.l_spectrum]
            macro spectrum ecx = eax
            ret
        """
        ren = self._renderer
        for l in self._lights_lst:
            l.L_asm(runtimes, visible_label, ren.assembler, ren.structures)
        for m in self._materials_lst:
            m.f_asm(runtimes, ren.assembler, ren.structures)

        #print (code)
        mc = ren.assembler.assemble(code, True) 
        name = "shade" + str(hash(self))
        for r in runtimes:
            ds = r.load(name, mc)
            ds["nlights"] = len(self._lights_lst)
            m_ptrs = [r.address_module(m.f_asm_name) for m in self._materials_lst]
            ds["materials_ptrs"] = tuple(m_ptrs)
            l_ptrs = [r.address_module(l.l_asm_name) for l in self._lights_lst]
            ds["lights_ptrs"] = tuple(l_ptrs)


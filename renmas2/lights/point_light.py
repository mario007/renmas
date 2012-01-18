from .light import Light

class PointLight(Light):
    def __init__(self, position, spectrum):
        self.position = position
        self.spectrum = spectrum

    def L(self, hitpoint, renderer):
        # 1. check visibility
        # 2. populate light vector in hitpoint and spectrum of light

        wi = self.position - hitpoint.hit_point
        wi.normalize()
        ndotwi = hitpoint.normal.dot(wi)
        hitpoint.wi = wi 
        hitpoint.ndotwi = ndotwi
        if ndotwi < 0.0: # ray strike back of object so that mean point is not visible to light. dielectric?? FIXME Think
            hitpoint.visible = False
            return False

        ret = renderer._intersector.visibility(self.position, hitpoint.hit_point)
        if ret:
            hitpoint.l_spectrum = self.spectrum #TODO reduce intesity, attenuation options  1/r^2
            hitpoint.visible = True
            return True
        else:
            hitpoint.visible = False
            return False

    #eax - pointer to hitpoint structure
    def L_asm(self, runtimes, visible_label, assembler, structures):

        code = """
            #DATA
        """
        code += structures.structs(('hitpoint',)) + """
        float position[4]
        spectrum l_spectrum
        float zero = 0.0
        uint32 ptr_hp
        float p1[4]
        float p2[4]
        #CODE
        mov dword [ptr_hp], eax ; save pointer to hitpoint
        macro eq128 xmm0 = position - eax.hitpoint.hit 
        macro normalization xmm0 {xmm6, xmm7}
        macro dot xmm1 = xmm0 * eax.hitpoint.normal {xmm6, xmm7}
        macro if xmm1 < zero goto reject  

        macro eq128 eax.hitpoint.wi = xmm0 {xmm0}
        macro eq32 eax.hitpoint.ndotwi = xmm1 {xmm1}
        ; test visibility of two points
        macro eq128 xmm0 = position
        macro eq128 xmm1 = eax.hitpoint.hit
        macro eq128 xmm0 = p1
        macro eq128 xmm1 = p2
        """
        code += "call " + visible_label + "\n" + """
        cmp eax, 1
        jne reject
        mov eax, dword [ptr_hp]
        mov dword [eax + hitpoint.visible], 1
        lea ecx, dword [eax + hitpoint.l_spectrum]
        mov ebx, l_spectrum
        macro spectrum ecx = ebx
        ret

        reject:
        mov eax, dword [ptr_hp]
        mov dword [eax + hitpoint.visible], 0
        ret
        """

        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        self.l_asm_name = name = "pointlight_L" + str(hash(self))
        self.ds = []
        for r in runtimes:
            self.ds.append(r.load(name, mc)) 
        self._populate_ds()

    def _populate_ds(self):
        for ds in self.ds:
            p = self.position
            ds["position"] = (p.x, p.y, p.z, 0.0)
            s = self.spectrum
            ds["l_spectrum.values"] = s.to_ds()

    def convert_spectrums(self, converter):
        self.spectrum = converter.convert_spectrum(self.spectrum, True)


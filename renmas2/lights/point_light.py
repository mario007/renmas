from .light import Light

class PointLight(Light):
    def __init__(self, position, spectrum, power=1.0):
        self._position = position
        self._spectrum = spectrum
        self._power = float(power)
        self._ds = []

    def _set_position(self, value):
        self._position = value
        self._populate_ds()
    def _get_position(self):
        return self._position
    position = property(_get_position, _set_position)

    def _set_spectrum(self, value):
        self._spectrum = value
        self._populate_ds()
    def _get_spectrum(self):
        return self._spectrum
    spectrum = property(_get_spectrum, _set_spectrum)

    def _set_power(self, value):
        self._power = float(value)
        self._populate_ds()
    def _get_power(self):
        return self._power
    power = property(_get_power, _set_power)

    def L(self, hitpoint, renderer):
        # 1. check visibility
        # 2. populate light vector in hitpoint and spectrum of light

        wi = self._position - hitpoint.hit_point
        wi.normalize()
        ndotwi = hitpoint.normal.dot(wi)
        hitpoint.wi = wi 
        hitpoint.ndotwi = ndotwi
        ndotwo = hitpoint.normal.dot(hitpoint.wo) #TODO remove this
        if ndotwi < 0.0:
            hitpoint.visible = False
            return False

        ret = renderer._intersector.visibility(self._position, hitpoint.hit_point)
        if ret:
            hitpoint.l_spectrum = self._spectrum * self._power #TODO reduce intesity, attenuation options  1/r^2
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
        self._ds = []
        for r in runtimes:
            self._ds.append(r.load(name, mc)) 
        self._populate_ds()

    def _populate_ds(self):
        for ds in self._ds:
            p = self._position
            ds["position"] = (p.x, p.y, p.z, 0.0)
            s = self._spectrum * self._power
            ds["l_spectrum.values"] = s.to_ds()

    def convert_spectrums(self, converter):
        self._spectrum = converter.convert_spectrum(self._spectrum, True)



from ..core.structures import SHADEPOINT 
from .light import Light

class PointLight(Light):
    def __init__(self, position, spectrum, scale=1.0):
        self._position = position
        self._spectrum = spectrum
        self._scale = float(scale)
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

    def _set_intesity_scale(self, value):
        self._scale = float(value)
        self._populate_ds()
    def _get_intesity_scale(self):
        return self._scale
    scale = property(_get_intesity_scale, _set_intesity_scale)

    def L(self, shadepoint):
        wi = self._position - shadepoint.hit
        scale = (1.0 / wi.length_squared()) * self._scale 
        spectrum = self._spectrum * scale
        wi.normalize()

        shadepoint.wi = wi
        shadepoint.light_position = self._position
        shadepoint.light_spectrum = spectrum

    #eax - pointer to shadepoint structure
    def L_asm(self, runtimes, assembler, spectrum_struct):
        structs = spectrum_struct + SHADEPOINT 
        #TODO - lea macro

        code = " #DATA \n" + structs + """
        uint32 mask[4] = 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0x00
        float position[4]
        spectrum light_spectrum
        float zero = 0.0
        float one = 1.0
        #CODE
        macro eq128 xmm0 = position - eax.shadepoint.hit 
        macro eq128 xmm5 = mask
        macro call andps xmm0, xmm5

        macro dot xmm1 = xmm0 * xmm0 {xmm6, xmm7}

        macro normalization xmm0 {xmm6, xmm7}
        macro eq128 eax.shadepoint.wi = xmm0 {xmm7}
        macro eq128 eax.shadepoint.light_position = position {xmm7}

        macro eq32 xmm2 = one / xmm1
        macro mov ebx, light_spectrum
        macro lea ecx, dword [eax + shadepoint.light_spectrum]
        macro spectrum ecx = xmm2 * ebx

        ret
        """
        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        self.light_asm_name = name = "pointlight" + str(id(self))
        self._ds = []
        for r in runtimes:
            self._ds.append(r.load(name, mc)) 
        self._populate_ds()

    def _populate_ds(self):
        for ds in self._ds:
            ds["position"] = self._position.to_ds()
            s = self._spectrum * self._scale
            ds["light_spectrum.values"] = s.to_ds()

    def convert_spectrums(self, mgr):
        self._spectrum = mgr.convert_spectrum(self._spectrum, True)


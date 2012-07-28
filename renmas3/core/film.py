import platform

from .image import ImageFloatRGBA
from .structures import SAMPLE

class Film:
    def __init__(self, width, height, renderer):
        self._image = ImageFloatRGBA(width, height)
        self._height = height
        self._renderer = renderer
        self._ds = None
        self.set_pass(0)

    def set_pass(self, n):
        self._current_pass = float(n)
        self._inv_pass = 1.0 / (float(n) + 1.0)
        self._populate_ds()

    def set_resolution(self, width, height):
        self._image = ImageFloatRGBA(width, height)
        self._height = height

    @property
    def image(self):
        return self._image

    #TODO -- currently only box filter are suported for now
    def add_sample(self, sample, spectrum):
        r, g, b = self._renderer.color_mgr.to_RGB(spectrum) 
        if r < 0.0: r = 0.0
        if g < 0.0: g = 0.0
        if b < 0.0: b = 0.0

        iy = self._height - sample.iy - 1 #flip the image
        r1, g1, b1, a1 = self._image.get_pixel(sample.ix, iy) 
        scaler = self._current_pass
        inv_scaler = self._inv_pass

        r = (r1 * scaler + r) * inv_scaler
        g = (g1 * scaler + g) * inv_scaler
        b = (b1 * scaler + b) * inv_scaler
        self._image.set_pixel(sample.ix, iy, r, g, b)

    def add_sample_asm(self, runtimes, label):
        #TODO 64-bit
        #eax - pointer to spectrum
        #ebx - pointer to sample 
        asm_structs = SAMPLE
        ASM = """
        #DATA
        """
        ASM += asm_structs + """
            float alpha_channel[4] = 0.0, 0.0, 0.0, 0.99
            uint32 height 
            uint32 ptr_buffer
            uint32 pitch_buffer
            uint32 mask[4] = 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0x00
            float scaler[4]
            float inv_scaler[4]

            #CODE
        """
        ASM += "global " + label + ":\n " + """
            push ebx
            """
        ASM += """macro call spectrum_to_rgb 

            macro eq128 xmm4 = mask
            macro call andps xmm0, xmm4
            macro eq128 xmm0 = xmm0 + alpha_channel
            macro call zero xmm5
            macro call maxps xmm0, xmm5

            ;flip the image and call set pixel
            pop ebx
            mov eax, dword [ebx + sample.ix]
            mov ecx, dword [ebx + sample.iy]
            mov ebx, dword [height] ;because of flipping image 
            sub ebx, ecx
            mov edx, dword [pitch_buffer]
            mov esi, dword [ptr_buffer]

            imul ebx, edx
            imul eax, eax, 16
            add eax, ebx
            add eax, esi
            macro eq128 xmm1 = eax
            macro eq128 xmm1 = xmm1 * scaler + xmm0
            macro eq128 xmm1 = xmm1 * inv_scaler
            macro eq128 eax = xmm1 {xmm7}
            
            ret

        """
        #TODO -- put alpha channel to 0.99 after xmm1 * inv_scaler
        mc = self._renderer.assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "film" + str(id(self))

        self._ds = []
        for r in runtimes:
            if not r.global_exists(label):
                self._ds.append(r.load(name, mc))

        self._populate_ds()

    def _populate_ds(self):
        if self._ds is None:
            return
        for ds in self._ds:
            width, height = self._image.size()
            ds["height"] = height - 1 
            scaler = self._current_pass
            inv_scaler = self._inv_pass
            ds["scaler"] = (scaler, scaler, scaler, 1.0)
            ds["inv_scaler"] = (inv_scaler, inv_scaler, inv_scaler, 1.0)

            addr, pitch = self._image.address_info()
            ds["ptr_buffer"] = addr
            ds["pitch_buffer"] = pitch



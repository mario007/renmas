
import time
import math
from .image import ImageRGBA, ImageFloatRGBA
from .blitter import Blitter
from .spectrum import Spectrum
import renmas2.switch as proc

#TODO make flip image as option
class Film:
    def __init__(self, width, height, nsamples, renderer):
        self._renderer = renderer
        self.width = width
        self.height = height
        self.nsamples = nsamples

        self.image = ImageFloatRGBA(width, height)
        self.frame_buffer = ImageRGBA(width, height)
        self.blitter = Blitter()
        self._ds = None

        self.spectrum = self._renderer.converter.zero_spectrum()
        self.curn = nsamples
        self.max_spectrum = self._renderer.converter.zero_spectrum()

        self._current_pass = 0.0 
        self._inv_pass = 1.0 / (0.0 + 1.0)

    def blt_image_to_buffer(self):
        da, dpitch = self.frame_buffer.get_addr()
        dw, dh = self.frame_buffer.get_size()
        sa, spitch = self.image.get_addr()
        sw, sh = self.image.get_size()
        self.blitter.blt_floatTorgba(da, 0, 0, dw, dh, dpitch, sa, 0, 0, sw, sh, spitch)

    def numsamples(self):
        return self.nsamples

    def set_pass(self, n):
        self._current_pass = float(n)
        self._inv_pass = 1.0 / (float(n) + 1.0)
        self._populate_ds()

    def set_resolution(self, width, height):
        self.width = width
        self.height = height
        self.image = ImageFloatRGBA(width, height)
        self.frame_buffer = ImageRGBA(width, height)
        self._populate_ds()

    def get_resolution(self):
        return (self.width, self.height)
        
    def set_nsamples(self, n):
        self.nsamples = n
        self.curn = n
        self.spectrum = self._renderer.converter.zero_spectrum()
        self._populate_ds()

    def reset(self):
        self.curn = self.nsamples 
        self.spectrum = self._renderer.converter.zero_spectrum()
        self._populate_ds()

    #TODO -- currently only box filter are suported
    def add_sample(self, sample, spectrum):
        r, g, b = self._renderer.converter.to_rgb(spectrum) 
        if r < 0.0: r = 0.0
        if g < 0.0: g = 0.0
        if b < 0.0: b = 0.0

        iy = self.height - sample.iy - 1 #flip the image
        r1, g1, b1, a1 = self.image.get_pixel(sample.ix, iy) 
        scaler = self._current_pass
        inv_scaler = self._inv_pass

        r = (r1 * scaler + r) * inv_scaler
        g = (g1 * scaler + g) * inv_scaler
        b = (b1 * scaler + b) * inv_scaler
        self.image.set_pixel(sample.ix, iy, r, g, b)
        
    def add_sample_asm(self, runtimes, label, label_spec_to_rgb):

        #eax - pointer to spectrum
        #ebx - pointer to sample 
        asm_structs = self._renderer.structures.structs(("hitpoint", "sample"))
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
        ASM += "call " + label_spec_to_rgb + """

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

        mc = self._renderer.assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "film" + str(hash(self))

        self._ds = []
        for r in runtimes:
            if not r.global_exists(label):
                self._ds.append(r.load(name, mc))

        self._populate_ds()

    def add_sample_old(self, sample, spectrum):
        if self.curn == 1:
            self.spectrum = self.spectrum + spectrum
            self.spectrum.scale(1.0/self.nsamples)
            #spec = self.spectrum

            #spec.clamp() #FIXME make clamp to certen color so to know when picture is wrong 
            iy = self.height - sample.iy - 1 #flip the image

            #print(sample.ix, iy, spec.r, spec.g, spec.b)
            #if spec.r > 0.99 or spec.g > 0.99 or spec.b > 0.99:
            #    print(spec)

            r, g, b = self._renderer.converter.to_rgb(self.spectrum) 
            if r < 0.0: r = 0.0
            if g < 0.0: g = 0.0
            if b < 0.0: b = 0.0
            #print (r, g, b)
            self.image.set_pixel(sample.ix, iy, r, g, b)
            self.curn = self.nsamples
            self.spectrum = self._renderer.converter.zero_spectrum()
        else:
            self.spectrum = self.spectrum + spectrum
            self.curn -= 1

 
    def add_sample_asm_old(self, runtimes, label, label_spec_to_rgb):

        #eax - pointer to spectrum
        #ebx - pointer to sample 
        asm_structs = self._renderer.structures.structs(("hitpoint", "sample"))
        ASM = """
        #DATA
        """
        ASM += asm_structs + """
            spectrum spec 
            float scale[4]
            float alpha_channel[4] = 0.0, 0.0, 0.0, 0.99
            uint32 nsamples 
            uint32 curn
            uint32 height 
            uint32 ptr_buffer
            uint32 pitch_buffer
            float clamp[4] = 0.99, 0.99, 0.99, 0.99
            float zero[4] = 0.0, 0.0, 0.0, 0.0
            uint32 mask[4] = 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0x00

            float temp[4]

            #CODE
        """
        ASM += "global " + label + ":\n " + """
            cmp dword [curn], 1
            jne _next_sample
            push ebx
            mov edx, spec
            macro spectrum edx = edx + eax 
            macro eq128 xmm0 = scale
            mov eax, spec
            macro spectrum eax = xmm0 * eax 
            """
        ASM += "call " + label_spec_to_rgb + """

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
            
            ;call set pixel  x = eax , y = ebx, ptr_buff = esi pitch = edx value = xmm0 
            mov esi, dword [ptr_buffer]
            mov edx, dword [pitch_buffer]
            macro call set_pixel

            ;remove this temp - this was just for testing --- think better test for this TODO
            macro eq128 temp = xmm0 {xmm0} 

            macro eq128 xmm0 = zero
            mov eax, spec
            macro spectrum eax = xmm0 * eax 
            mov edx, dword [nsamples]
            mov dword [curn], edx
            ret

            _next_sample:
            mov edx, spec
            macro spectrum edx = edx + eax 
            sub dword [curn], 1
            ret

        """

        mc = self._renderer.assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "film" + str(hash(self))

        self._ds = []
        for r in runtimes:
            if not r.global_exists(label):
                self._ds.append(r.load(name, mc))

        self._populate_ds()

    def _populate_ds(self):
        if self._ds is None: return
        for ds in self._ds:
            ds["height"] = self.height - 1 
            scaler = self._current_pass
            inv_scaler = self._inv_pass
            ds["scaler"] = (scaler, scaler, scaler, 1.0)
            ds["inv_scaler"] = (inv_scaler, inv_scaler, inv_scaler, 1.0)

            addr, pitch = self.image.get_addr()
            ds["ptr_buffer"] = addr
            ds["pitch_buffer"] = pitch

    def _populate_ds_old(self):
        if self._ds is None: return
        for ds in self._ds:
            spec = self._renderer.converter.zero_spectrum()
            ds["spec.values"] = spec.to_ds()
            ds["nsamples"] = self.nsamples
            ds["curn"] = self.curn
            scale =  1.0 / self.nsamples
            ds["scale"] = (scale, scale, scale, 0.0)
            ds["height"] = self.height - 1 

            addr, pitch = self.image.get_addr()
            ds["ptr_buffer"] = addr
            ds["pitch_buffer"] = pitch


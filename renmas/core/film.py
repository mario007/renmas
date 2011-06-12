
import renmas.gui
import renmas
import renmas.utils as util

#TODO make flip image as option
class Film:
    def __init__(self, width, height, nsamples=1):
        self.width = width
        self.height = height
        self.nsamples = nsamples

        self.image = renmas.gui.ImageFloatRGBA(width, height)

        self.spectrum = renmas.core.Spectrum(0.0, 0.0, 0.0)
        self.curn = nsamples
        self.ds = None

    def numsamples(self):
        return self.nsamples

    def set_resolution(width, height):
        self.width = width
        self.height = height
        #TODO - new image is needed FIXME
        
    def set_nsamples(self, n):
        self.nsamples = n
        self.curn = n
        self.spectrum = renmas.core.Spectrum(0.0, 0.0, 0.0)
        self._populate_ds()

    def reset(self):
        self.curn = self.nsamples 
        self.spectrum = renmas.core.Spectrum(0.0, 0.0, 0.0)
        self._populate_ds()

    def add_sample(self, sample, hitpoint):
        if self.curn == 1:
            self.spectrum = self.spectrum + hitpoint.spectrum
            self.spectrum.scale(1.0/self.nsamples)
            spec = self.spectrum

            #spec.clamp() FIXME make clamp to certen color so to know when picture is wrong 
            iy = self.height - sample.iy - 1 #flip the image

            #print(sample.ix, iy, spec.r, spec.g, spec.b)
            self.image.set_pixel(sample.ix, iy, spec.r, spec.g, spec.b)
            self.curn = self.nsamples
            self.spectrum = renmas.core.Spectrum(0.0, 0.0, 0.0)
        else:
            self.spectrum = self.spectrum + hitpoint.spectrum
            self.curn -= 1

    def add_sample_asm(self, runtime, label):

        lbl_name = "set_pixel" + str(hash(self))        
        self.image.set_pixel_asm(runtime, lbl_name)

        #eax - pointer to hitpoint structure
        #ebx - pointer to sample structure
        asm_structs = renmas.utils.structs("hitpoint", "sample")
        ASM = """
        #DATA
        """
        ASM += asm_structs + """
            float spectrum[4]
            float scale[4]
            float zero_spectrum[4] = 0.0, 0.0, 0.0, 0.0
            uint32 nsamples 
            uint32 curn
            uint32 height 

            #CODE
        """
        ASM += "global " + label + ":\n " + """
            cmp dword [curn], 1
            jne _next_sample
            macro eq128 xmm0 = spectrum + eax.hitpoint.spectrum
            macro eq128 xmm0 = xmm0 * scale 

            ;flip the image and call set pixel
            mov eax, dword [ebx + sample.ix]
            mov ecx, dword [ebx + sample.iy]
            mov ebx, dword [height] ;because of flipping image 
            sub ebx, ecx
            
            ;call set pixel  x = eax , y = ebx, value = xmm0 
        """
        ASM += "call " + lbl_name + "\n" + """
            mov edx, dword [nsamples]
            macro eq128 spectrum = zero_spectrum
            mov dword [curn], edx
            ret

            _next_sample:
            macro eq128 spectrum = spectrum + eax.hitpoint.spectrum
            sub dword [curn], 1
            ret

        """

        assembler = util.get_asm()
        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "film" + str(util.unique())
        self.ds = runtime.load(name, mc)
        self._populate_ds()

    def _populate_ds(self):
        if self.ds is None: return
        s = self.spectrum
        self.ds["spectrum"] = (s.r, s.g, s.b, 0.0)
        self.ds["nsamples"] = self.nsamples
        self.ds["curn"] = self.curn
        scale =  1.0 / self.nsamples
        self.ds["scale"] = (scale, scale, scale, 0.0)
        self.ds["height"] = self.height - 1 



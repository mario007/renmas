
import renmas.gui
import renmas
import renmas.utils as util
import math

#TODO make flip image as option
class Film:
    def __init__(self, width, height, nsamples=1):
        self.width = width
        self.height = height
        self.nsamples = nsamples

        self.image = renmas.gui.ImageFloatRGBA(width, height)
        self.frame_buffer = renmas.gui.ImageRGBA(width, height)
        self.blitter = renmas.gui.Blitter()

        self.spectrum = renmas.core.Spectrum(0.0, 0.0, 0.0)
        self.curn = nsamples
        self.ds = None
        self.max_spectrum = renmas.core.Spectrum(0.0, 0.0, 0.0)

    def blt_image_to_buffer(self):
        da, dpitch = self.frame_buffer.get_addr()
        dw, dh = self.frame_buffer.get_size()
        sa, spitch = self.image.get_addr()
        sw, sh = self.image.get_size()
        self.blitter.blt_floatTorgba(da, 0, 0, dw, dh, dpitch, sa, 0, 0, sw, sh, spitch)

    def numsamples(self):
        return self.nsamples

    def set_resolution(self, width, height):
        self.width = width
        self.height = height
        self.image = renmas.gui.ImageFloatRGBA(width, height)
        self.frame_buffer = renmas.gui.ImageRGBA(width, height)
        # you need again to build runtime object
        #TODO - think better solution if its needed

    def get_resolution(self):
        return (self.width, self.height)
        
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

            self.max_spectrum.r = max(self.max_spectrum.r, spec.r)
            self.max_spectrum.g = max(self.max_spectrum.g, spec.g)
            self.max_spectrum.b = max(self.max_spectrum.b, spec.b)

            #spec.clamp() #FIXME make clamp to certen color so to know when picture is wrong 
            iy = self.height - sample.iy - 1 #flip the image

            #print(sample.ix, iy, spec.r, spec.g, spec.b)
            #if spec.r > 0.99 or spec.g > 0.99 or spec.b > 0.99:
            #    print(spec)
            self.image.set_pixel(sample.ix, iy, spec.r, spec.g, spec.b)
            self.curn = self.nsamples
            self.spectrum = renmas.core.Spectrum(0.0, 0.0, 0.0)
        else:
            self.spectrum = self.spectrum + hitpoint.spectrum
            self.curn -= 1

    def tone_map(self):
        width, height = self.image.get_size()
        delta = 0.001
        sum_pix = 0.0
        lw_min = 100000.0
        lw_max = 0.0
        for j in range(height):
            for i in range(width):
                r, g, b, a = self.image.get_pixel(i, j)
                lw = 0.27 * r + 0.67 * g + 0.06 * b
                lw_min = min(lw_min, lw)
                lw_max = max(lw_max, lw)
                lw += delta
                sum_pix += math.log(lw)

        if lw_min == 0.0: lw_min = 0.001
        lw_min_log2 = math.log(lw_min, 2)
        lw_max_log2 = math.log(lw_max, 2)
        log_av = math.exp(sum_pix / float(width*height))

        den = 2.0 * math.log(log_av, 2) - lw_min_log2 - lw_max_log2
        nom = lw_max_log2 - lw_min_log2
        alpha = 0.18 * math.pow(4.0, den/nom)

        lwhite = 1.5 * math.pow(2.0, lw_max_log2 - lw_min_log2 - 5.0)

        print("Log_average", log_av, lw_min, lw_max)
        print("alpha = ", alpha, "  Lwhite = ", lwhite)

        rd_max = gd_max = bd_max = 0.0
        r_max = g_max = b_max = 0.0

        scaling = alpha / log_av
        for j in range(height):
            for i in range(width):
                r, g, b, a = self.image.get_pixel(i, j)
                r_max = max(r, r_max)
                g_max = max(g, g_max)
                b_max = max(b, b_max)

                lw = 0.27 * r + 0.67 * g + 0.06 * b
                lw += delta

                lx = scaling * lw 
                ldisp = (lx * (1 + lx / (lwhite*lwhite))) / (1.0 + lx)
                rd = ldisp * r / lw
                gd = ldisp * g / lw
                bd = ldisp * b / lw

                rd_max = max(rd, rd_max)
                gd_max = max(gd, gd_max)
                bd_max = max(bd, bd_max)

                if rd > 0.99: rd = 0.99
                if bd > 0.99: bd = 0.99
                if gd > 0.99: gd = 0.99

                self.image.set_pixel(i, j, rd, gd, bd)

        print(rd_max, gd_max, bd_max)
        print(r_max, g_max, b_max)


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
            float alpha_channel[4] = 0.0, 0.0, 0.0, 0.99
            uint32 nsamples 
            uint32 curn
            uint32 height 
            float clamp[4] = 0.99, 0.99, 0.99, 0.99

            #CODE
        """
        ASM += "global " + label + ":\n " + """
            cmp dword [curn], 1
            jne _next_sample
            macro eq128 xmm0 = spectrum + eax.hitpoint.spectrum
            macro eq128 xmm0 = xmm0 * scale 
            ;because of alpha channel - try solve this in better way
            macro eq128 xmm0 = xmm0 + alpha_channel
            ; for clamping 
            ;minps xmm0, oword [clamp] 

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



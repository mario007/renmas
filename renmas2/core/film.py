
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

    def add_sample(self, sample, spectrum):
        if self.curn == 1:
            self.spectrum = self.spectrum + spectrum
            self.spectrum.scale(1.0/self.nsamples)
            #spec = self.spectrum

            #self.max_spectrum.r = max(self.max_spectrum.r, spec.r)
            #self.max_spectrum.g = max(self.max_spectrum.g, spec.g)
            #self.max_spectrum.b = max(self.max_spectrum.b, spec.b)

            #spec.clamp() #FIXME make clamp to certen color so to know when picture is wrong 
            iy = self.height - sample.iy - 1 #flip the image

            #print(sample.ix, iy, spec.r, spec.g, spec.b)
            #if spec.r > 0.99 or spec.g > 0.99 or spec.b > 0.99:
            #    print(spec)

            r, g, b = self._renderer.converter.to_rgb(self.spectrum) 
            #TODO tone - mapping process
            if r < 0.0: r = 0.0
            if g < 0.0: g = 0.0
            if b < 0.0: b = 0.0
            if r > 0.99: r = 0.99
            if g > 0.99: g = 0.99
            if b > 0.99: b = 0.99
            #print (r, g, b)
            self.image.set_pixel(sample.ix, iy, r, g, b)
            self.curn = self.nsamples
            self.spectrum = self._renderer.converter.zero_spectrum()
        else:
            self.spectrum = self.spectrum + spectrum
            self.curn -= 1

    def tone_map2(self):
        width, height = self.image.get_size()
        sum_lw = 0.0
        for j in range(height):
            for i in range(width):
                r, g, b, a = self.image.get_pixel(i, j)
                lw = 0.27 * r + 0.67 * g + 0.06 * b + 0.00001
                sum_lw += math.log(lw)
        sum_lw = sum_lw / (width*height)
        sum_lw = math.exp(sum_lw)
        lav = 0.18 / sum_lw

        for j in range(height):
            for i in range(width):
                r, g, b, a = self.image.get_pixel(i, j)
                lw = 0.27 * r + 0.67 * g + 0.06 * b + 0.00001
                l = lav *  lw
                ldisp = l / (1+l)
                rd = ldisp * r / lw
                gd = ldisp * g / lw
                bd = ldisp * b / lw

                if rd > 0.99: rd = 0.99
                if bd > 0.99: bd = 0.99
                if gd > 0.99: gd = 0.99
                self.image.set_pixel(i, j, rd, gd, bd, 0.99)




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
                lw += delta
                lw_min = min(lw_min, lw)
                lw_max = max(lw_max, lw)
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
                #rd = ldisp * r / lw
                #gd = ldisp * g / lw
                #bd = ldisp * b / lw

                rd = ldisp * math.pow(r / lw, 0.8)
                gd = ldisp * math.pow(g / lw, 0.8)
                bd = ldisp * math.pow(b / lw, 0.8)

                rd_max = max(rd, rd_max)
                gd_max = max(gd, gd_max)
                bd_max = max(bd, bd_max)

                if rd > 0.99: rd = 0.99
                if bd > 0.99: bd = 0.99
                if gd > 0.99: gd = 0.99

                self.image.set_pixel(i, j, rd, gd, bd)

        print(rd_max, gd_max, bd_max)
        print(r_max, g_max, b_max)


    def add_sample_asm(self, runtimes, label, label_spec_to_rgb):

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

            ;because of alpha channel - try solve this in better way , pxor xmm0, xmm0 da postavis na nulu
            macro eq128 xmm0 = xmm0 + alpha_channel
            """
        if proc.AVX:
            ASM += """
            ; for clamping 
            vmaxps xmm0, xmm0, oword [zero]
            vminps xmm0, xmm0, oword [clamp] 
            """
        else:
            ASM += """
            maxps xmm0, oword [zero]
            minps xmm0, oword [clamp] 
            """
        ASM += """

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



import renmas.utils as util

class RegularSampler:
    def __init__(self, width, height, pixel=1.0):
        #resolution of image
        self.pix_size = pixel
        self.ds = None
        self.resolution(width, height)

    def resolution(self, width, height):
        self.width = width
        self.height = height

        #precompute -width/2 + 0.5 and -height/2 + 0.5 
        self.w2 = -float(width) / 2.0 + 0.5
        self.h2 = -float(height) / 2.0 + 0.5
        self.tile(0, 0, width, height)

    def pixel_size(self, size):
        self.pix_size = size
        self._populate_ds()

    def get_pixel_size(self):
        return self.pix_size

    def tile(self, x, y, width, height):
        width -= 1
        height -= 1
        self.tilex = x
        self.tiley = y
        self.tilew = width 
        self.tileh = height 
        
        self.tile_endx = self.tilex + width 
        self.tile_endy = self.tiley + height 
        self.curx = x - 1
        self.cury = y
        self._populate_ds()

    def reset(self):
        self.tile(self.tilex, self.tiley, self.tilew, self.tileh)

    def get_sample(self, sample):
        # xw = s(x - width/2 + 0.5)
        # yw = s(y - height/2 + 0.5)
        if self.curx == self.tile_endx:
            if self.cury == self.tile_endy:
                return None #end of sampling
            else:
                self.cury += 1
            self.curx = self.tilex
        else:
            self.curx += 1

        sample.x = self.pix_size * (self.curx + self.w2)  
        sample.y = self.pix_size * (self.cury + self.h2)
        sample.ix = self.curx
        sample.iy = self.cury
        return True

    def nsamples(self):
        return 1

    def set_samples_per_pixel(self, num):
        pass

    def get_sample_asm(self, runtime, label):
        # eax - pointer to sample structure
        if util.AVX:
            line1 = "vcvtdq2ps xmm0, xmm0 \n"
        else:
            line1 = "cvtdq2ps xmm0, xmm0 \n"

        asm_structs = util.structs("sample")
        code = """
            #DATA
        """
        code += asm_structs + """
            uint32 tile_endx, tile_endy
            uint32 tilex, tiley
            uint32 cur_xyxy[4] ; we just use first two numbers for now
            float pixel_size[4]
            float w2h2[4]

            #CODE
        """
        code += " global " + label + ":\n" + """
            mov ebx, dword [cur_xyxy]
            cmp ebx, dword [tile_endx]
            je _checky
            ; increase curx 
            add ebx, 1
            mov dword [cur_xyxy], ebx
            ; calculate sample
           
            macro eq128 xmm0 = cur_xyxy
        """
        code += line1 + """
            macro eq128_128 xmm1 = pixel_size, xmm2 = w2h2
            macro eq128 xmm3 = xmm0 + xmm2 {xmm1}
            mov ecx, dword [cur_xyxy + 4]
            macro eq128 eax.sample.xyxy = xmm3 * xmm1
            mov dword [eax + sample.ix] ,ebx
            mov dword [eax + sample.iy] ,ecx
            mov eax, 1
            ret

            _checky:
            mov ecx, dword [cur_xyxy + 4]
            cmp ecx, dword [tile_endy]
            je _end_sampling
            ; increase cury
            add ecx, 1
            mov ebx, dword [tilex]
            mov dword [cur_xyxy+ 4], ecx 
            mov dword [cur_xyxy], ebx
            macro eq128 xmm0 = cur_xyxy
        """
        code += line1 + """
            macro eq128_128 xmm1 = pixel_size, xmm2 = w2h2
            macro eq128 xmm3 = xmm0 + xmm2 {xmm1}
            macro eq128 eax.sample.xyxy = xmm3 * xmm1
            mov dword [eax + sample.ix] ,ebx
            mov dword [eax + sample.iy] ,ecx
            mov eax, 1
            ret

            _end_sampling:
            xor eax, eax 
            ret

        """
        assembler = util.get_asm()
        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "get_sample" + str(util.unique())
        self.ds = runtime.load(name, mc)
        self._populate_ds()
        return True

    def _populate_ds(self):
        if self.ds is None: return
        self.ds["tile_endx"] = self.tile_endx 
        self.ds["tile_endy"] = self.tile_endy 
        self.ds["tilex"] = self.tilex
        self.ds["tiley"] = self.tiley
        self.ds["cur_xyxy"] = (self.curx, self.cury, self.curx, self.cury)
        self.ds["pixel_size"] = (self.pix_size, self.pix_size, self.pix_size, self.pix_size)
        self.ds["w2h2"] = (self.w2, self.h2, self.w2, self.h2)



class RegularSamplerOld:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.curx = x - 1 
        self.cury = y
        self.ds = None

    def get_sample(self):
        if self.curx == self.x + self.width:
            if self.cury == self.y + self.height:
                return None #end of sampling
            else:
                self.cury += 1
            self.curx = self.x
        else:
            self.curx += 1

        return (float(self.curx) + 0.5, float(self.cury) + 0.5)

    def reset(self):
        self.curx = self.x - 1
        self.cury = self.y 
        if self.ds is not None:
            self.ds["curxy"] = (self.curx, self.cury, self.curx, self.cury)

    def nsamples(self): #samples per pixel
        return 1

    def generate_asm(self, runtime, name_label):
        #TEST if label exist in runtime, generate exception if exist
        asm = Tdasm()
        asm_code = """
        #DATA
        uint32 curxy[4]
        uint32 x, y, width, height

        #CODE 
        global """ + name_label + ": \n" 

        asm_code += """
        ;we generate 0.5 in xmm0 = 0.5, 0.5, 0.5, 0.5
        pcmpeqw xmm0, xmm0
        pslld xmm0, 26
        psrld xmm0, 2

        mov eax, dword [curxy]
        cmp eax, dword [width] 
        je _testy
        add dword [curxy], 1
        movdqa xmm1, oword [curxy] 
        cvtdq2ps xmm1, xmm1
        addps xmm0, xmm1
        mov ecx, dword [curxy]
        mov edx, dword [curxy + 4]
        """
        asm_code += "call " + self.filt.calc_name() + """
        mov eax, 1
        ret

        _testy:
        mov eax, dword [curxy + 4]
        cmp eax, dword [height]
        je _end_sampling
        add dword [curxy + 4], 1
        mov ebx, dword [x]
        mov dword [curxy], ebx 
        movdqa xmm1, oword [curxy] 
        cvtdq2ps xmm1, xmm1
        addps xmm0, xmm1
        mov ecx, dword [curxy]
        mov edx, dword [curxy + 4]
        """
        asm_code += "call " + self.filt.calc_name() + """
        mov eax, 1
        ret

        _end_sampling:
        mov eax, 0
        ret
        """
        mc = asm.assemble(asm_code, True)
        name = "regular_sampler" 
        self.ds = runtime.load(name, mc)
        self.ds["x"] = self.x
        self.ds["y"] = self.y
        self.ds["curxy"] = (self.curx, self.cury, self.curx, self.cury)
        self.ds["width"] = self.x + self.width
        self.ds["height"] = self.y + self.height



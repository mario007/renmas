
import random
import renmas.utils as util

class RandomSampler:
    def __init__(self, width, height, n=1, pixel=1.0):
        #resolution of image
        self.pix_size = pixel
        self.n = n
        self.ds = None
        self.resolution(width, height)

    def resolution(self, width, height):
        #precompute -width/2  and -height/2  
        self.width = width
        self.height = height
        self.w2 = -float(width) / 2.0 
        self.h2 = -float(height) / 2.0 
        self.tile(0, 0, width, height)


    def pixel_size(self, size):
        self.pix_size = size
        self._populate_ds()

    def tile(self, x, y, width, height):
        width -= 1
        height -= 1
        self.tilex = x
        self.tiley = y
        self.tilew = width 
        self.tileh = height 
        
        self.tile_endx = self.tilex + width 
        self.tile_endy = self.tiley + height 
        self.curx = x 
        self.cury = y
        self.curn = self.n 
        self._populate_ds()

    def reset(self):
        self.curn = self.n
        self.tile(self.tilex, self.tiley, self.tilew, self.tileh)

    def get_sample(self, sample):
        # xw = s(x - width/2 + px) 
        # yw = s(y - height/2 + py)

        if self.curn > 0:
            sample.x = self.pix_size * (self.curx + self.w2 + random.random())  
            sample.y = self.pix_size * (self.cury + self.h2 + random.random())
            sample.ix = self.curx
            sample.iy = self.cury
            self.curn -= 1
            return True
        else:
            self.curn = self.n - 1 
            if self.curx == self.tile_endx:
                if self.cury == self.tile_endy:
                    return None #end of sampling
                else:
                    self.cury += 1
                self.curx = self.tilex
            else:
                self.curx += 1

        sample.x = self.pix_size * (self.curx + self.w2 + random.random())  
        sample.y = self.pix_size * (self.cury + self.h2 + random.random())
        sample.ix = self.curx
        sample.iy = self.cury
        return True

    def nsamples(self):
        return self.n 

    def get_sample_asm(self, runtime, label):
        # eax - pointer to sample structure
        util.load_func(runtime, "random")

        if util.AVX:
            line1 = "vcvtdq2ps xmm4, xmm4 \n"
        else:
            line1 = "cvtdq2ps xmm4, xmm4 \n"

        asm_structs = util.structs("sample")
        code = """
            #DATA
        """
        code += asm_structs + """
            uint32 n, curn
            uint32 tile_endx, tile_endy
            uint32 tilex, tiley
            uint32 cur_xyxy[4] ; we just use first two numbers for now
            float pixel_size[4]
            float w2h2[4]

            #CODE
        """
        code += " global " + label + ":\n" + """
            cmp dword [curn], 0
            jbe _next_pixel

            ; calculate sample
            call random
            ; random number is in xmm0
            macro eq128 xmm4 = cur_xyxy {xmm0}
            """
        code += line1 + """
            macro eq128_128 xmm1 = pixel_size, xmm2 = w2h2 {xmm0}
            macro eq128 xmm3 = xmm4 + xmm2 {xmm1, xmm0}
            macro eq128 xmm3 = xmm3 + xmm0 {xmm1}
            mov ebx, dword [cur_xyxy]
            mov ecx, dword [cur_xyxy + 4]
            macro eq128 eax.sample.xyxy = xmm3 * xmm1
            mov dword [eax + sample.ix] ,ebx
            mov dword [eax + sample.iy] ,ecx
            sub dword [curn], 1
            mov eax,  1 
            ret
            
            
            _next_pixel:
            mov edx, dword [n] ; self.curn = self.n - 1
            sub edx, 1
            mov dword [curn], edx

            mov ebx, dword [cur_xyxy]
            cmp ebx, dword [tile_endx]
            je _checky
            ; increase curx 
            add ebx, 1
            mov dword [cur_xyxy], ebx
            ; calculate sample
           
            call random
            macro eq128 xmm4 = cur_xyxy {xmm0}
        """
        code += line1 + """
            macro eq128_128 xmm1 = pixel_size, xmm2 = w2h2 {xmm0}
            macro eq128 xmm3 = xmm4 + xmm2 {xmm1, xmm0}
            macro eq128 xmm3 = xmm3 + xmm0 {xmm1}
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

            call random
            macro eq128 xmm4 = cur_xyxy {xmm0}
        """
        code += line1 + """
            macro eq128_128 xmm1 = pixel_size, xmm2 = w2h2 {xmm0}
            macro eq128 xmm3 = xmm4 + xmm2 {xmm1, xmm0}
            macro eq128 xmm3 = xmm3 + xmm0 {xmm1}
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
        self.ds["n"] = self.n
        self.ds["curn"] = self.curn



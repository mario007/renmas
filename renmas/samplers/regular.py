
from tdasm import Tdasm


class RegularSampler:
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



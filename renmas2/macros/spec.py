
import renmas2.switch as proc

class MacroSpectrum:
    def __init__(self, renderer):
        self.renderer = renderer
        self.xmm_regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]
        self.ymm_regs = ["ymm0", "ymm1", "ymm2", "ymm3", "ymm4", "ymm5", "ymm6", "ymm7"]

    def macro_spectrum(self, asm, tokens):
        if len(tokens) == 0: return
        if len(tokens) == 5:
            r1, equal, r2, operator, r3 = tokens
            if r2 in self.xmm_regs:
                return self._scaling_spectrum(asm, tokens)
        return self._arithmetic_spectrum(asm, tokens)

    def _scaling_spectrum(self, asm, tokens):
        sampled = self.renderer.spectrum_rendering
        n = self.renderer.nspectrum_samples
        r1, equal, xmm, mul, r3 = tokens
        code = ""
        if proc.AVX:
            code = "vshufps " + xmm + ", " + xmm + ", " + xmm + ", 0x00 \n"
            ymm = "y" + xmm[1:]
            code += "vperm2f128 ymm7, " + ymm + ", " + ymm + ", 0x00 \n"
        else:
            code = "shufps " + xmm + ", " + xmm + ", 0x00 \n"
            code += "movaps xmm7, " + xmm + "\n"
        if proc.AVX:
            if sampled:
                off = 0
                while n > 0:
                    rounds = n // 8
                    if n > 56: rounds = 7
                    code += self._expand()
                    code += self._command(r3, "*", rounds, None, off)
                    code += self._command(r1, "mov", rounds, False, off)
                    n = n - 56
                    off += 224
            else:
                code = "vshufps " + xmm + ", " + xmm + ", " + xmm + ", 0x00 \n" 
                code += "vmulps " + xmm + ", " +  xmm + ", oword[" + r3 + " + spectrum.values]\n"  
                code += "vmovaps oword[" + r1 + " + spectrum.values], " + xmm + "\n"
        else:
            if sampled:
                off = 0
                while n > 0:
                    rounds = n // 4
                    if n > 28: rounds = 7
                    code += self._expand()
                    code += self._command(r3, "*", rounds, None, off)
                    code += self._command(r1, "mov", rounds, False, off)
                    n = n - 28
                    off += 112
            else:
                code = "shufps " + xmm + ", " + xmm + ", 0x00 \n"
                code += "mulps " + xmm + ", oword[" + r3 + " + spectrum.values]\n"  
                code += "movaps oword[" + r1 + " + spectrum.values], " + xmm + "\n"
        return code

    def _expand(self):
        ## vmovaps ymm0, ymm7 BUG in Tdasm that must be resolved
        if proc.AVX:
            code = """
                        ;vmovaps yword [re], ymm7
                        vmovaps ymm0, ymm7
                        ;vmovaps ymm7, ymm0
                        vmovaps yword [re], ymm7
                        #END
                        vmovaps ymm1, ymm7
                        vmovaps ymm2, ymm0
                        vmovaps ymm3, ymm1
                        vmovaps ymm4, ymm0
                        vmovaps ymm5, ymm1
                        vmovaps ymm6, ymm0
            """
        else:
            code = """ movaps xmm0, xmm7
                        movaps xmm1, xmm7
                        movaps xmm2, xmm0
                        movaps xmm3, xmm1
                        movaps xmm4, xmm0
                        movaps xmm5, xmm1
                        movaps xmm6, xmm0
            """
        return code

    def _arithmetic_spectrum(self, asm, tokens):
        assign = False
        if len(tokens) == 3:
            r1, equal, r2 = tokens
            assign = True
        elif len(tokens) == 5:
            r1, equal, r2, operator, r3 = tokens
        
        sampled = self.renderer.spectrum_rendering
        n = self.renderer.nspectrum_samples
        code = ""
        if proc.AVX:
            if sampled:
                off = 0
                while n > 0:
                    rounds = n // 8
                    if n > 64: rounds = 8
                    code += self._command(r2, "mov", rounds, True, off)
                    if not assign:
                        code += self._command(r3, operator, rounds, None, off)
                    code += self._command(r1, "mov", rounds, False, off)
                    n = n - 64 
                    off += 256 
            else:
                code = "vmovaps xmm0, oword[" + r2 + " + spectrum.values] \n"
                if not assign:
                    com = "vaddps "
                    if operator == "-": com = "vsubps "
                    if operator == "*": com = "vmulps "
                    code += com + " xmm0, xmm0, oword[" + r3 + " + spectrum.values] \n"
                code += "vmovaps oword[" + r1 + " + spectrum.values], xmm0 \n"
        else:
            if sampled:
                off = 0
                while n > 0:
                    rounds = n // 4
                    if n > 32: rounds = 8
                    code += self._command(r2, "mov", rounds, True, off)
                    if not assign:
                        code += self._command(r3, operator, rounds, None, off)
                    code += self._command(r1, "mov", rounds, False, off)
                    n = n - 32
                    off += 128 
            else:
                code = "movaps xmm0, oword[" + r2 + " + spectrum.values] \n"
                if not assign:
                    com = "addps "
                    if operator == "-": com = "subps "
                    if operator == "*": com = "mulps "
                    code += com + " xmm0, oword[" + r3 + " + spectrum.values] \n"
                code += "movaps oword[" + r1 + " + spectrum.values], xmm0 \n"

        return code

    def _command(self, reg, command, n, to_reg, off):
        code = ""
        if command == "mov":
            if proc.AVX:
                mov = "vmovaps "
                regs = self.ymm_regs
                size = " yword"
            else:
                mov = "movaps "
                regs = self.xmm_regs
                size = " oword"

            for i in range(n):
                if to_reg:
                    code += mov + regs[i] + " ," + size + "[" + reg + " + spectrum.values +" + str(off) + "] \n"
                else:
                    code += mov + size + "[" + reg + " + spectrum.values + " + str(off) + "], " + regs[i] +" \n"

                if proc.AVX: off += 32 
                else: off += 16 
        if command == "+" or command == "-" or command == "*":
            if proc.AVX:
                com = "vaddps "
                if command == "-": com = "vsubps "
                if command == "*": com = "vmulps "
                regs = self.ymm_regs
            else:
                com = "addps "
                if command == "-": com = "subps "
                if command == "*": com = "mulps "
                regs = self.xmm_regs

            for i in range(n):
                if proc.AVX:
                    code += com + regs[i] + "," + regs[i] + ", yword[" + reg + " + spectrum.values +" + str(off) + "]\n" 
                else:
                    code += com + regs[i] + ", oword[" + reg + " + spectrum.values +" + str(off) + "]\n" 
                if proc.AVX: off += 32 
                else: off += 16 
        return code


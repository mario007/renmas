
import renmas2.switch as proc

class MacroSpectrum:
    def __init__(self, renderer):
        self.renderer = renderer

    def macro_spectrum(self, asm, tokens):
        if len(tokens) == 0: return
        return self._arithmetic_spectrum(asm, tokens)

    def _arithmetic_spectrum(self, asm, tokens):
        assign = False
        if len(tokens) == 3:
            r1, equal, r2 = tokens
            assign = True
        elif len(tokens) == 5:
            r1, equal, r2, operator, r3 = tokens
        
        sampled = self.renderer.spectrum_rendering
        n = self.renderer.nspectrum_samples
        xmm_regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]
        ymm_regs = ["ymm0", "ymm1", "ymm2", "ymm3", "ymm4", "ymm5", "ymm6", "ymm7"]
        code = ""
        if proc.AVX:
            if sampled:
                off = 0
                while n > 0:
                    rounds = n // 8
                    if n > 64: rounds = 8
                    if assign:
                        code += self._command(r2, "mov", rounds, True, off)
                        code += self._command(r1, "mov", rounds, False, off)
                    else:
                        code += self._command(r2, "mov", rounds, True, off)
                        code += self._command(r3, operator, rounds, None, off)
                        code += self._command(r1, "mov", rounds, False, off)
                    n = n - 64 
                    off += 256 
            else:
                code = "vmovaps xmm0, oword[" + r2 + " + spectrum.values] \n"
                code += "vaddps xmm0, xmm0, oword[" + r3 + " + spectrum.values] \n"
                code += "vmovaps oword[" + r1 + " + spectrum.values], xmm0 \n"
        else:
            if sampled:
                off = 0
                while n > 0:
                    rounds = n // 4
                    if n > 32: rounds = 8
                    if assign:
                        code += self._command(r2, "mov", rounds, True, off)
                        code += self._command(r1, "mov", rounds, False, off)
                    else:
                        code += self._command(r2, "mov", rounds, True, off)
                        code += self._command(r3, operator, rounds, None, off)
                        code += self._command(r1, "mov", rounds, False, off)
                    n = n - 32
                    off += 128 
            else:
                code = "movaps xmm0, oword[" + r2 + " + spectrum.values] \n"
                code += "addps xmm0, oword[" + r3 + " + spectrum.values] \n"
                code += "movaps oword[" + r1 + " + spectrum.values], xmm0 \n"

        return code

    def _command(self, reg, command, n, to_reg, off):
        xmm_regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]
        ymm_regs = ["ymm0", "ymm1", "ymm2", "ymm3", "ymm4", "ymm5", "ymm6", "ymm7"]
        code = ""
        if command == "mov":
            if proc.AVX:
                mov = "vmovaps "
                regs = ymm_regs
                size = " yword"
            else:
                mov = "movaps "
                regs = xmm_regs
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
                regs = ymm_regs
            else:
                com = "addps "
                if command == "-": com = "subps "
                if command == "*": com = "mulps "
                regs = xmm_regs

            for i in range(n):
                if proc.AVX:
                    code += com + regs[i] + "," + regs[i] + ", yword[" + reg + " + spectrum.values +" + str(off) + "]\n" 
                else:
                    code += com + regs[i] + ", oword[" + reg + " + spectrum.values +" + str(off) + "]\n" 
                if proc.AVX: off += 32 
                else: off += 16 
        return code



import renmas2.switch as proc

# macro cross xmm1 x xmm2 {xmm6, xmm7}  - result is in xmm1
def cross_product(self, tokens):
    xmm1, dummy1, xmm2, dummy2, tmp1, dummy3, tmp2, dummy4 = tokens

    ASM = "\n#CODE \n"
    ASM += "macro eq128 " + tmp1 + " = " + xmm1 + "\n" 
    ASM += "macro eq128 " + tmp2 + " = " + xmm2 + "\n"
    if proc.AVX:
        ASM += "vshufps " + xmm1 + "," + xmm1 + ","  + xmm1 + ", 0xC9 \n" 
        ASM += "vshufps " + xmm2 + "," + xmm2 + ","  + xmm2 + ", 0xD2 \n" 
        ASM += "macro eq128 " + xmm1 + " = " + xmm1 + "*" + xmm2 + " \n" 
        ASM += "vshufps " + tmp1 + "," + tmp1 + ","  + tmp1 + ", 0xD2 \n" 
        ASM += "vshufps " + tmp2 + "," + tmp2 + ","  + tmp2 + ", 0xC9 \n" 
    else:
        ASM += "shufps " + xmm1 + ","  + xmm1 + ", 0xC9 \n" 
        ASM += "shufps " + xmm2 + ","  + xmm2 + ", 0xD2 \n" 
        ASM += "macro eq128 " + xmm1 + " = " + xmm1 + "*" + xmm2 + " \n" 
        ASM += "shufps " + tmp1 + ","  + tmp1 + ", 0xD2 \n" 
        ASM += "shufps " + tmp2 + ","  + tmp2 + ", 0xC9 \n" 

    ASM += "macro eq128 " + tmp1 + " = " + tmp1 + " * " + tmp2 + "\n"
    ASM += "macro eq128 " + xmm1 + " = " + xmm1 + " - " + tmp1 + "\n"

    return ASM


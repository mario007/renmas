
import renmas2.switch as proc

# macro normalization xmm5 {xmm6, xmm7}
def normalization(asm, tokens):
    
    xmm, dummy1, tmp1, dummy2, tmp2, dummy3 = tokens

    line0 = """
    #CODE
    """
    line1 = line2 = line3 = ""
    if proc.AVX:
        line1 = "vdpps " + tmp1 + "," + xmm + "," +  xmm + ", 0x7f \n"
        line2 = "vsqrtps " + tmp1 + "," + tmp1 + "\n"
    elif proc.SSE41:
        line1 = "movaps " + tmp1 + "," +  xmm + "\n"
        line2 = "dpps " + tmp1 + "," +  tmp1 + ", 0x7F\n" 
        line3 = "sqrtps " + tmp1 + "," + tmp1 + "\n"
    else:
        line1 = "macro dot " + tmp1 + " = " + xmm + "*" + xmm + " { " + tmp1 + "," + tmp2 + " }\n"
        line2 = "macro broadcast " + tmp1 + " = " + tmp1 + "[0]\n"
        line3 = "sqrtps " + tmp1 + "," + tmp1 + "\n"
    line4 = "macro eq128 " + xmm + " = " + xmm + "/" + tmp1 + "\n"

    code = line0 + line1 + line2 + line3 + line4 
    return code


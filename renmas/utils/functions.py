
from tdasm import Tdasm
import renmas.core
from renmas.core import AsmStructures


asm = Tdasm()
AVX = asm.avx_supported()
AVX = False 

SSSE3 = asm.cpu["ssse3"]
#SSSE3 = False
SSE3 = asm.cpu["sse3"]
SSE41 = asm.cpu["sse41"]
#SSE41 = False
SSE2 = asm.cpu["sse2"]

def structs(*lst_structs):
    code = ""
    asm_structs = AsmStructures()

    for s in lst_structs:
        struct = asm_structs.get_struct(s)
        if struct is None:
           raise ValueError("Structure " + str(s) + " doesn't exist!")
        code += struct

    return code
    
assembler = None

def get_asm():

    from renmas.macros import eq32, eq128, eq32_32, eq32_128, eq128_128, eq128_32
    from renmas.macros import dot_product, macro_if, broadcast
    global assembler
    if assembler is None:
        assembler = Tdasm()
        assembler.register_macro("eq128", eq128)
        assembler.register_macro("eq32", eq32)

        assembler.register_macro("eq128_32", eq128_32)
        assembler.register_macro("eq32_128", eq32_128)
        assembler.register_macro("eq128_128", eq128_128)
        assembler.register_macro("eq32_32", eq32_32)

        assembler.register_macro("dot", dot_product)
        assembler.register_macro("if", macro_if)
        assembler.register_macro("broadcast", broadcast)

    return assembler

NUM = -1 
def unique():
    global NUM
    NUM += 1
    return NUM

# dynamic loadr of functions written in assembly 
# support functions have defined name
def load_func(runtime, *names):

    for name in names:
        if not runtime.global_exists(name):
            if name == "random":
                renmas.core.Rng.random_float(runtime, "random")
            elif name == "fast_pow_ss":
                renmas.maths.load_math_func("fast_pow_ss", runtime)
            elif name == "fast_pow_ps":
                renmas.maths.load_math_func("fast_pow_ps", runtime)
            elif name == "fast_tan_ss":
                renmas.maths.load_math_func("fast_tan_ss", runtime)
            elif name == "fast_tan_ps":
                renmas.maths.load_math_func("fast_tan_ps", runtime)
            elif name == "fast_cos_ps":
                renmas.maths.load_math_func("fast_cos_ps", runtime)
            elif name == "fast_cos_ss":
                renmas.maths.load_math_func("fast_cos_ss", runtime)
            elif name == "fast_sin_ss":
                renmas.maths.load_math_func("fast_sin_ss", runtime)
            elif name == "fast_sin_ps":
                renmas.maths.load_math_func("fast_sin_ps", runtime)
            elif name == "fast_acos_ss":
                renmas.maths.load_math_func("fast_acos_ss", runtime)
            elif name == "fast_acos_ps":
                renmas.maths.load_math_func("fast_acos_ps", runtime)
            elif name == "fast_exp_ps":
                renmas.maths.load_math_func("fast_exp_ps", runtime)
            elif name == "fast_exp_ss":
                renmas.maths.load_math_func("fast_exp_ss", runtime)
            elif name == "fast_sincos_ps":
                renmas.maths.load_math_func("fast_sincos_ps", runtime)
            elif name == "fast_sincos_ss":
                renmas.maths.load_math_func("fast_sincos_ss", runtime)
            elif name == "ray_triangle_mesh":
                #renmas.shapes.intersect_ray_triangle(runtime, "ray_triangle_mesh")
                #renmas.shapes.intersect_ray_triangle_avx(runtime, "ray_triangle_mesh")
                renmas.shapes.intersect_ray_triangle_new(runtime, "ray_triangle_mesh")
            pass # load that function

def normalization(xmm, tmp1, tmp2):
    line0 = """
    #CODE
    """
    line1 = line2 = line3 = ""
    if AVX:
        line1 = "vdpps " + tmp1 + "," + xmm + "," +  xmm + ", 0x7f \n"
        line2 = "vsqrtps " + tmp1 + "," + tmp1 + "\n"
    elif SSE41:
        line1 = "movaps " + tmp1 + "," +  xmm + "\n"
        line2 = "dpps " + tmp1 + "," +  tmp1 + ", 0x7F\n" 
        line3 = "sqrtps " + tmp1 + "," + tmp1 + "\n"
    else:
        line1 = "macro dot " + tmp1 + " = " + xmm + "*" + xmm + "\n"
        line2 = "macro broadcast " + tmp1 + " = " + tmp1 + "[0]\n"
        line3 = "sqrtps " + tmp1 + "," + tmp1 + "\n"
    line4 = "macro eq128 " + xmm + " = " + xmm + "/" + tmp1 + "\n"

    code = line0 + line1 + line2 + line3 + line4 
    return code

# xmm1 x xmm2  - result is in xmm1
def cross_product(xmm1, xmm2, tmp1, tmp2):

    ASM = "\n#CODE \n"
    ASM += "macro eq128 " + tmp1 + " = " + xmm1 + "\n" 
    ASM += "macro eq128 " + tmp2 + " = " + xmm2 + "\n"
    if AVX:
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


blitter = None
def memcpy(da, sa, n):
    global blitter
    if blitter is None:
        blitter = renmas.gui.Blitter()
    n = n // 4 #FIXME - fix this better
    blitter._memcpy(da, sa, n)

## cof_fi = N dot L
def fresnel_nk(n, k, cos_fi):
    pass


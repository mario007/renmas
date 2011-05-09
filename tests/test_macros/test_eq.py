
from tdasm import Tdasm, Runtime
from renmas.macros import eq32, eq128, eq32_32, eq32_128, eq128_128, eq128_32
from renmas.macros import dot_product, macro_if

ASM = """
#DATA
float v1[4] = 1.0, 1.5, 2.0, 3.0
float v2[4] = 1.0, 2.5, 3.0, 4.0
float v3[4] = 1.0, 5.5, 1.0, 2.0
float v4[4] = 1.0, 5.5, 1.0, 2.0
float v5[4] = 1.0, 5.5, 1.0, 2.0
float v6[4] = 1.0, 5.5, 1.0, 2.0
float v7[4] 
#CODE
    macro eq128 xmm3 = v3  
    macro eq128 xmm2 = v2
    macro eq128 xmm5 = v1 - xmm3 
    macro eq128_128 v7 = xmm3 * v3, v6 = v1 + v2 
#END
"""

if __name__ == "__main__":
    asm = Tdasm()
    asm.register_macro("eq128", eq128)
    asm.register_macro("eq32", eq32)
    asm.register_macro("eq128_32", eq128_32)
    asm.register_macro("eq32_32", eq32_32)
    asm.register_macro("eq128_128", eq128_128)
    asm.register_macro("dot", dot_product)
    asm.register_macro("if", macro_if)

    mc = asm.assemble(ASM)
    mc.print_machine_code()

    runtime = Runtime()
    ds = runtime.load("test", mc)
    runtime.run("test")
    print(ds["v6"])
    print(ds["v7"])



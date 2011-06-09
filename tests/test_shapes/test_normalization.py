
from tdasm import Runtime
import renmas
import renmas.maths
import renmas.utils as util

ASM = """
    #DATA
    float v1[4] = 2.2, 3.3, 4.4, 0.0
    #CODE
    movaps xmm0, oword [v1]

"""    
code = util.normalization("xmm0", "xmm1", "xmm2")

ASM += code + """
    movaps oword [v1], xmm0
"""

if __name__ == "__main__":
    print(ASM)

    asm = util.get_asm()
    mc = asm.assemble(ASM)
    runtime = Runtime()
    ds = runtime.load("test", mc)
    runtime.run("test")
    print(ds["v1"])

    v = renmas.maths.Vector3(2.2, 3.3, 4.4)
    v.normalize()
    print(v)



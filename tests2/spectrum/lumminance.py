
import unittest
from random import random
from tdasm import Runtime
import renmas2


class LumminanceTest(unittest.TestCase):
    def setUp(self):
        pass

    def asm_code1(self, ren):
        code = """
        #DATA
        """
        code += ren.structures.structs(("spectrum",)) + """
        spectrum sp1
        float Y
        #CODE
        mov eax, sp1
        call lumminance
        macro eq32 Y = xmm0 {xmm0}
        #END
        """
        return code

    def test_Y(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()

        ren.spectral_rendering = True
        conv = ren.converter
        conv.Y_asm("lumminance", [runtime])
        spec1 = conv.create_spectrum((0.66,0.88, 0.11))

        mc = ren.assembler.assemble(self.asm_code1(ren))
        ds = runtime.load("test", mc)
        ds["sp1.values"] = spec1.to_ds()
        runtime.run("test")

        self.assertAlmostEqual(conv.Y(spec1), ds["Y"], 4)

if __name__ == "__main__":
    unittest.main()


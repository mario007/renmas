
import unittest
from random import random
from tdasm import Runtime
from renmas3.base import ColorManager
from renmas3.macros import create_assembler


class LuminanceTest(unittest.TestCase):
    def setUp(self):
        pass

    def asm_code1(self, mgr):
        code = """
        #DATA
        """
        code += mgr.spectrum_asm_struct() + """
        Spectrum sp1
        float Y
        #CODE
        macro mov eax, sp1
        call luminance
        macro eq32 Y = xmm0 {xmm0}
        #END
        """
        return code

    def test_Y_rgb(self):
        mgr = ColorManager(False)
        runtime = Runtime()

        mgr.Y_asm([runtime])
        spec1 = mgr.create_spectrum((0.66,0.88, 0.11))

        mc = create_assembler().assemble(self.asm_code1(mgr))
        ds = runtime.load("test", mc)
        ds["sp1.values"] = spec1.to_ds()
        runtime.run("test")
        
        self.assertAlmostEqual(mgr.Y(spec1), ds["Y"], 4)

    def test_Y_spectrum(self):
        mgr = ColorManager()
        runtime = Runtime()

        mgr.Y_asm([runtime])
        spec1 = mgr.create_spectrum((0.66,0.88, 0.11))

        mc = create_assembler().assemble(self.asm_code1(mgr))
        #mc.print_machine_code()
        ds = runtime.load("test", mc)
        ds["sp1.values"] = spec1.to_ds()
        runtime.run("test")

        self.assertAlmostEqual(mgr.Y(spec1), ds["Y"], 4)

if __name__ == "__main__":
    unittest.main()


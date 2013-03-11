
import unittest
from random import random
from tdasm import Runtime
from renmas3.base import ColorManager
from renmas3.macros import create_assembler


class SpectrumToRGBTest(unittest.TestCase):
    def setUp(self):
        pass

    def asm_code1(self, mgr):
        code = """
        #DATA
        """
        code += mgr.spectrum_asm_struct() + """
        Spectrum sp1
        float rgb[4]
        #CODE
        macro mov eax, sp1
        call spectrum_to_rgb 
        macro eq128 rgb = xmm0 {xmm7}
        #END
        """
        return code

    def test_spectrum_to_rgb1(self):
        mgr = ColorManager(False)
        runtime = Runtime()

        mgr.to_RGB_asm([runtime])
        spec1 = mgr.create_spectrum((0.66,0.88, 0.11))

        mc = create_assembler().assemble(self.asm_code1(mgr))
        ds = runtime.load("test", mc)
        ds["sp1.values"] = spec1.to_ds()
        runtime.run("test")
        
        rgb = mgr.to_RGB(spec1)
        rgb2 = ds['rgb']

        self.assertAlmostEqual(rgb.r, rgb2[0], 4)
        self.assertAlmostEqual(rgb.g, rgb2[1], 4)
        self.assertAlmostEqual(rgb.b, rgb2[2], 4)

    def test_spectrum_to_rgb2(self):
        mgr = ColorManager()
        runtime = Runtime()

        mgr.to_RGB_asm([runtime])
        spec1 = mgr.create_spectrum((0.66,0.88, 0.11))

        mc = create_assembler().assemble(self.asm_code1(mgr))
        ds = runtime.load("test", mc)
        ds["sp1.values"] = spec1.to_ds()
        runtime.run("test")
        
        rgb = mgr.to_RGB(spec1)
        rgb2 = ds['rgb']

        self.assertAlmostEqual(rgb.r, rgb2[0], 4)
        self.assertAlmostEqual(rgb.g, rgb2[1], 4)
        self.assertAlmostEqual(rgb.b, rgb2[2], 4)


if __name__ == "__main__":
    unittest.main()


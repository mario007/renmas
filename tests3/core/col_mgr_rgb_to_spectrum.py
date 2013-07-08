
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
        macro eq128 xmm0 = rgb
        call rgb_to_spectrum
        macro eq128 rgb = xmm0 {xmm7}
        #END
        """
        return code

    def test_spectrum_to_rgb1(self):
        mgr = ColorManager(False)
        runtime = Runtime()

        mgr.rgb_to_sampled_asm([runtime], 'rgb_to_spectrum')
        spec1 = mgr.create_spectrum((0.66,0.88, 0.11))

        mc = create_assembler().assemble(self.asm_code1(mgr))
        ds = runtime.load("test", mc)

        ds["rgb"] = spec1.to_ds()

        runtime.run("test")

        rgb = ds["sp1.values"]

        self.assertAlmostEqual(spec1.r, rgb[0], 4)
        self.assertAlmostEqual(spec1.g, rgb[1], 4)
        self.assertAlmostEqual(spec1.b, rgb[2], 4)

    def test_spectrum_to_rgb2(self):
        mgr = ColorManager(spectral=True)
        runtime = Runtime()

        mgr.rgb_to_sampled_asm([runtime], 'rgb_to_spectrum')
        spec1 = mgr.create_spectrum((0.66,0.88, 0.11))

        mc = create_assembler().assemble(self.asm_code1(mgr))
        ds = runtime.load("test", mc)

        ds["rgb"] = (0.66, 0.88, 0.11, 0.00)
        runtime.run("test")
        
        vals = ds['sp1.values']
        
        for i in range(len(vals)):
            self.assertAlmostEqual(vals[i], spec1.samples[i], 4)


if __name__ == "__main__":
    unittest.main()



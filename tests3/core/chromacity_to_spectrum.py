
import unittest
from random import random
from tdasm import Runtime
from renmas3.base import ColorManager
from renmas3.macros import create_assembler

class ChromacityToSpectrumTest(unittest.TestCase):
    def setUp(self):
        pass

    def asm_code1(self, mgr):
        code = """
        #DATA
        """
        code += mgr.spectrum_asm_struct() + """
        Spectrum sp1
        float x, y
        #CODE
        macro mov eax, sp1
        macro eq32 xmm0 = x
        macro eq32 xmm1 = y
        call chromacity_to_spectrum
        #END
        """
        return code

    def test_chromacity_to_spectrum(self):
        mgr = ColorManager(spectral=False)
        runtime = Runtime()

        mgr.chromacity_to_spectrum_asm([runtime], 'chromacity_to_spectrum')
        mc = create_assembler().assemble(self.asm_code1(mgr))
        ds = runtime.load("test", mc)
        ds['x'] = 0.45
        ds['y'] = 0.41

        spec = mgr.chromacity_to_spectrum(0.45, 0.41)

        runtime.run("test")
        rgb = ds['sp1.values']

        self.assertAlmostEqual(spec.r, rgb[0], 4)
        self.assertAlmostEqual(spec.g, rgb[1], 4)
        self.assertAlmostEqual(spec.b, rgb[2], 4)

    def test_chromacity_to_spectrum2(self):
        mgr = ColorManager(spectral=True)
        runtime = Runtime()

        mgr.chromacity_to_spectrum_asm([runtime], 'chromacity_to_spectrum')
        mc = create_assembler().assemble(self.asm_code1(mgr))
        ds = runtime.load("test", mc)
        ds['x'] = 0.45
        ds['y'] = 0.41

        spec = mgr.chromacity_to_spectrum(0.45, 0.41)
        runtime.run("test")

        vals = ds['sp1.values']
        for i in range(len(vals)):
            self.assertAlmostEqual(vals[i], spec.samples[i], 4)

if __name__ == "__main__":
    unittest.main()


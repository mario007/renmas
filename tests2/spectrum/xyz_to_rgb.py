
import unittest
from tdasm import Runtime
import renmas2


class XYZ_TO_RGBTest(unittest.TestCase):
    def setUp(self):
        pass

    def asm_code1(self, ren):
        code = """
        #DATA
        float XYZ[4] 
        float RGB[4]
        #CODE
        macro eq128 xmm0 = XYZ
        call xyz_to_rgb 
        macro eq128 RGB = xmm0 {xmm7}
        #END
        """
        return code

    def test_Y(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()

        ren.spectral_rendering = True
        conv = ren.converter
        conv.xyz_to_rgb_asm("xyz_to_rgb", [runtime], ren.assembler)

        mc = ren.assembler.assemble(self.asm_code1(ren))
        ds = runtime.load("test", mc)

        ds["XYZ"] = (0.69, 0.78, 0.88, 0.00)
        runtime.run("test")
        ret1 = ds["RGB"]
        ret2 = ren.converter.xyz_to_rgb(0.69, 0.78, 0.88)

        self.assertAlmostEqual(ret1[0], ret2[0], 4)
        self.assertAlmostEqual(ret1[1], ret2[1], 4)
        self.assertAlmostEqual(ret1[2], ret2[2], 4)

if __name__ == "__main__":
    unittest.main()


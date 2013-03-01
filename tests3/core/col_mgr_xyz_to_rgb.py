
import unittest
from random import random
from tdasm import Runtime
from renmas3.base import ColorManager
from renmas3.macros import create_assembler

class XYZ_TO_RGBTest(unittest.TestCase):
    def setUp(self):
        pass

    def asm_code1(self):
        code = """
        #DATA
        float XYZ[4] 
        float RGB[4]
        #CODE
        macro eq128 xmm0 = XYZ
        call XYZ_to_RGB 
        macro eq128 RGB = xmm0 {xmm7}
        #END
        """
        return code

    def test_Y(self):
        mgr = ColorManager(False)
        runtime = Runtime()

        mgr.XYZ_to_RGB_asm([runtime])
        mc = create_assembler().assemble(self.asm_code1())
        ds = runtime.load("test", mc)

        ds["XYZ"] = (0.69, 0.78, 0.88, 0.00)
        runtime.run("test")
        ret1 = ds["RGB"]
        ret2 = mgr.XYZ_to_RGB(0.69, 0.78, 0.88)

        self.assertAlmostEqual(ret1[0], ret2[0], 4)
        self.assertAlmostEqual(ret1[1], ret2[1], 4)
        self.assertAlmostEqual(ret1[2], ret2[2], 4)

if __name__ == "__main__":
    unittest.main()


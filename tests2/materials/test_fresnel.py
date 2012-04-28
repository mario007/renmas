
import unittest
from random import random
from tdasm import Runtime
import renmas2

class FresnelTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_fresnel(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()

        silver = ren.spd.load("metal", "silver")
        n = ren.converter.create_spectrum(silver[0])
        k = ren.converter.create_spectrum(silver[1])
        spec = ren.converter.create_spectrum([(500,1.3), (600,1.4), (700,1.5)])
        print(spec)

        n, k = renmas2.materials.FresnelConductor.conv_f0(n)
        fresnel = renmas2.materials.FresnelConductor(n=n, k=k)
        


if __name__ == "__main__":
    unittest.main()



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
        fresnel = renmas2.materials.Fresnel(n=n, k=k)


if __name__ == "__main__":
    unittest.main()


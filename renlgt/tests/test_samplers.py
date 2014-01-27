
import unittest
from renlgt.samplers import RegularSampler
from renlgt.renderer import Renderer

rne = Renderer()


class SamplerTest(unittest.TestCase):
    def test_regular_sampler(self):
        sam = RegularSampler(2, 2, 1.0, 1)
        sam.create_shader()
        sam.prepare_standalone()

        sample = sam.generate_sample()
        self._check_result(sample, -0.5, -0.5, 0.5, 0.5, 0, 0, 1)
        sample = sam.generate_sample()
        self._check_result(sample, 0.5, -0.5, 0.5, 0.5, 1, 0, 1)
        sample = sam.generate_sample()
        self._check_result(sample, -0.5, 0.5, 0.5, 0.5, 0, 1, 1)
        sample = sam.generate_sample()
        self._check_result(sample, 0.5, 0.5, 0.5, 0.5, 1, 1, 1)

        sample = sam.generate_sample()
        self.assertFalse(sample)

    def _check_result(self, sample, x, y, px, py, ix, iy, weight):
        self.assertAlmostEqual(sample.x, x)
        self.assertAlmostEqual(sample.y, y)
        self.assertAlmostEqual(sample.px, px)
        self.assertAlmostEqual(sample.py, py)
        self.assertEqual(sample.ix, ix)
        self.assertEqual(sample.iy, iy)
        self.assertAlmostEqual(sample.weight, weight)


if __name__ == "__main__":
    unittest.main()

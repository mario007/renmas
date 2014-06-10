
import unittest
from tdasm import Runtime

from sdl.spectrum import RGBSpectrum, SampledSpectrum, create_samples, SampledManager
from sdl.shader import Shader
from sdl.args import RGBArg, SampledArg


class SpectrumTests(unittest.TestCase):

    def test_rgb_spectrum(self):
        code = """
spec = Spectrum(0.23)
        """
        spec = RGBArg('spec', RGBSpectrum(0.2, 0.3, 0.4))
        shader = Shader(code=code, args=[spec])
        shader.compile()
        runtime = Runtime()
        shader.prepare([runtime])
        shader.execute()

        val = shader.get_value('spec')
        self.assertAlmostEqual(val.r, 0.23)
        self.assertAlmostEqual(val.g, 0.23)
        self.assertAlmostEqual(val.b, 0.23)

    def test_sampled_spectrum(self):
        code = """
spec = Spectrum(0.23)
        """

        vals = [(450, 0.13), (480, 0.45), (620, 0.58)]
        samples = create_samples(vals, 32, 400, 700)
        sam_spec = SampledSpectrum(samples)
        spec = SampledArg('spec', sam_spec)

        shader = Shader(code=code, args=[spec])
        shader.compile(color_mgr=SampledManager())
        runtime = Runtime()
        shader.prepare([runtime])
        shader.execute()

        val = shader.get_value('spec')
        for i in range(len(val.samples)):
            self.assertAlmostEqual(val.samples[i], 0.23)


if __name__ == "__main__":
    unittest.main()

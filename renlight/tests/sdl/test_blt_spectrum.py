
import unittest
from tdasm import Runtime

from renlight.spectrum import RGBSpectrum, SampledSpectrum, create_samples
from renlight.sdl.shader import Shader
from renlight.sdl.args import RGBArg, SampledArg


class SpectrumTests(unittest.TestCase):

    def test_rgb_spectrum(self):
        code = """
spec2 = Spectrum(spec, 0.23)
        """
        spec = RGBArg('spec', RGBSpectrum(0.2, 0.3, 0.4))
        spec2 = RGBArg('spec2', RGBSpectrum(0.0, 0.0, 0.0))
        shader = Shader(code=code, args=[spec, spec2])
        shader.compile()
        runtime = Runtime()
        shader.prepare([runtime])
        shader.execute()

        val = shader.get_value('spec2')
        self.assertAlmostEqual(val.r, 0.23)
        self.assertAlmostEqual(val.g, 0.23)
        self.assertAlmostEqual(val.b, 0.23)

    def test_sampled_spectrum(self):

        code = """
spec2 = Spectrum(spec, 0.23)
        """

        vals = [(450, 0.13), (480, 0.45), (620, 0.58)]
        samples = create_samples(vals, 32, 400, 700)
        sam_spec = SampledSpectrum(samples)
        spec = SampledArg('spec', sam_spec)

        vals = [(450, 0.11)]
        samples = create_samples(vals, 32, 400, 700)
        sam_spec = SampledSpectrum(samples)
        spec2 = SampledArg('spec2', sam_spec)

        shader = Shader(code=code, args=[spec, spec2])
        shader.compile()
        runtime = Runtime()
        shader.prepare([runtime])
        shader.execute()

        val = shader.get_value('spec2')
        for i in range(len(val.samples)):
            self.assertAlmostEqual(val.samples[i], 0.23)


if __name__ == "__main__":
    unittest.main()


import unittest
from tdasm import Runtime

from renlight.vector import Vector3
from renlight.spectrum import RGBSpectrum, SampledManager, SampledSpectrum,\
    create_samples
from renlight.renderer.spec_shaders import rgb_to_vec_shader,\
    sampled_to_vec_shader
from renlight.sdl.shader import Shader
from renlight.sdl.args import RGBArg, SampledArg, Vec3Arg


class ConvSpecTests(unittest.TestCase):

    def test_rgb_spec_to_vec(self):

        shader = rgb_to_vec_shader()
        shader.compile()
        runtime = Runtime()
        shader.prepare([runtime])

        code = """
rez = spectrum_to_vec(r1)
        """
        s = RGBArg('r1', RGBSpectrum(0.2, 0.3, 0.4))
        rez = Vec3Arg('rez', Vector3(0.0, 0.0, 0.0))
        shader2 = Shader(code=code, args=[rez, s])
        shader2.compile([shader])
        shader2.prepare([runtime])
        shader2.execute()

        val = shader2.get_value('rez')
        self.assertAlmostEqual(val.x, 0.2)
        self.assertAlmostEqual(val.y, 0.3)
        self.assertAlmostEqual(val.z, 0.4)

    def test_sampled_spec_to_vec(self):
        mgr = SampledManager()
        shader = sampled_to_vec_shader(mgr)
        shader.compile()
        runtime = Runtime()
        shader.prepare([runtime])
        code = """
rez = spectrum_to_vec(r1)
        """

        vals = [(450, 0.13), (480, 0.45), (620, 0.58)]
        samples = create_samples(vals, 32, 400, 700)
        sam_spec = SampledSpectrum(samples)
        s = SampledArg('r1', sam_spec)

        rez = Vec3Arg('rez', Vector3(0.0, 0.0, 0.0))
        shader2 = Shader(code=code, args=[rez, s])
        shader2.compile([shader])
        shader2.prepare([runtime])
        shader2.execute()

        val = shader2.get_value('rez')
        conv = mgr.sampled_to_rgb(sam_spec)

        self.assertAlmostEqual(val.x, conv.r, places=6)
        self.assertAlmostEqual(val.y, conv.g, places=6)
        self.assertAlmostEqual(val.z, conv.b, places=6)


if __name__ == "__main__":
    unittest.main()

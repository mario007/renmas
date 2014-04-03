
import unittest
import math
from tdasm import Runtime
from renlgt.material import Material, MaterialManager
from renlgt.shadepoint import register_rgb_shadepoint
from sdl import Shader, SampledManager, RGBSpectrum, RGBArg,\
    FloatArg, Vec3Arg, Vector3


def cos_hemisphere(r1, r2, normal, e=1.0):

    phi = 2.0 * 3.14159 * r1
    exponent = 1.0 / (e + 1.0)
    cos_theta = pow(r2, exponent)

    tmp = 1.0 - cos_theta * cos_theta
    sin_theta = math.sqrt(tmp)
    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)
    pu = sin_theta * cos_phi 
    pv = sin_theta * sin_phi
    pw = cos_theta

    w = normal 
    tv = Vector3(0.0034, 1.0, 0.0071)
    v = tv.cross(w)
    v.normalize()
    u = v.cross(w)

    ndir = u * pu + v * pv + w * pw
    ndir.normalize()
    return ndir


class MaterialMgrTest(unittest.TestCase):

    def test_material_manager(self):
        sam_mgr = SampledManager()
        register_rgb_shadepoint()

        runtimes = [Runtime(), Runtime()]
        mat = Material()
        mat.load('lambertian', sam_mgr, spectral=False)
        mat.set_value('diffuse', RGBSpectrum(0.2, 0.3, 0.4))

        mgr = MaterialManager()
        mgr.add('material1', mat)

        mgr.compile_shaders(sam_mgr, spectral=False)
        mgr.prepare_shaders(runtimes)

        code = """
hp = HitPoint()
sp = ShadePoint()
material_reflectance(hp, sp, 0)
spec = sp.material_reflectance
        """
        spec = RGBArg('spec', RGBSpectrum(0.5, 0.5, 0.5))
        shader = Shader(code=code, args=[spec])
        shader.compile(shaders=[mgr.ref_shader])
        shader.prepare(runtimes)
        shader.execute()

        s = shader.get_value('spec')
        ls = RGBSpectrum(0.2, 0.3, 0.4) * (1.0 / math.pi)

        self.assertAlmostEqual(s.r, ls.r)
        self.assertAlmostEqual(s.g, ls.g)
        self.assertAlmostEqual(s.b, ls.b)

    def test_material_sampling_manager(self):
        sam_mgr = SampledManager()
        register_rgb_shadepoint()

        runtimes = [Runtime(), Runtime()]
        mat = Material()
        mat.load('lambertian', sam_mgr, spectral=False)
        mat.set_value('diffuse', RGBSpectrum(0.2, 0.3, 0.4))

        mgr = MaterialManager()
        mgr.add('material1', mat)

        mgr.compile_shaders(sam_mgr, spectral=False)
        mgr.prepare_shaders(runtimes)

        code = """
hp = HitPoint()
hp.normal = (0.1, 0.4, 0.66)
hp.normal = normalize(hp.normal)
sp = ShadePoint()
material_sampling(hp, sp, 0)
pdf = sp.pdf
wi = sp.wi
        """
        pdf = FloatArg('pdf', 0.0)
        wi = Vec3Arg('wi', Vector3(0.0, 0.0, 0.0))
        shader = Shader(code=code, args=[pdf, wi])
        shader.compile(shaders=[mgr.sampling_shader])
        shader.prepare(runtimes)
        shader.execute()

        s = shader.get_value('pdf')
        print(s)
        s = shader.get_value('wi')
        print(s)
        normal = Vector3(0.1, 0.4, 0.66)
        normal.normalize()
        print(cos_hemisphere(r1=0.1, r2=0.06, normal=normal,e=1.0))

if __name__ == "__main__":
    unittest.main()


import unittest
import math
import random
from tdasm import Runtime
from renlgt.material import Material, MaterialManager
from renlgt.shadepoint import register_rgb_shadepoint
from sdl import Shader, SampledManager, RGBSpectrum, RGBArg,\
    FloatArg, Vec3Arg, Vector3
from renlgt.shader_lib import shaders_functions

shaders_functions()

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


def reflect(normal, incident):
    cosi = -normal.dot(incident)
    return incident + 2.0 * cosi * normal


def tir(normal, incident, n1, n2):
    n = n1 / n2
    cosi = -normal.dot(incident)
    sint2 = n * n * (1.0 - cosi * cosi)
    if sint2 > 1.0:  # TIR
        return 1
    return 0


def refract(normal, incident, n1, n2):
    n = n1 / n2
    cosi = -normal.dot(incident)
    sint2 = n * n * (1.0 - cosi * cosi)
    if sint2 > 1.0:  # TIR
        return Vector(0.0, 0.0, 0.0)
    cost = math.sqrt(1.0 - sint2)
    return n * incident + (n * cosi - cost) * normal


def dielectric_reflectance(normal, incident, n1, n2):
    n = n1 / n2
    cosi = -normal.dot(incident)
    sint2 = n * n * (1.0 - cosi * cosi)
    if sint2 > 1.0:  # TIR
        return 1.0
    cost = math.sqrt(1.0 - sint2)
    rorth = (n1 * cosi - n2 * cost) / (n1 * cosi + n2 * cost)
    rpar = (n2 * cosi - n1 * cost) / (n2 * cosi + n1 * cost)
    return (rorth * rorth + rpar * rpar) * 0.5


def sampling_glass(ior, wo, normal):

    incident = wo * -1.0
    n1 = 1.0
    n2 = ior

    ndotwo = normal.dot(wo)
    if ndotwo < 0.0:
        normal = normal * -1.0
        n1 = ior
        n2 = 1.0

    ret = tir(normal, incident, n1, n2)
    if ret == 1:  # TIR ocur
        wi = reflect(normal, incident)
        pdf = 1.0
        reflectance = RGBSpectrum(1.0, 1.0, 1.0)
        print("TIR ocured")
    else:
        rnd = random.random()
        rnd = 0.3

        k = 0.5
        R = dielectric_reflectance(normal, incident, n1, n2)
        P = (1.0 - k) * R + 0.5 * k
        print(R, P, n1, n2)
        print("ACOS", math.degrees(math.acos(normal.dot(wo))))
        # R = 1.0
        # P = 1.0

        if rnd < P: # reflection ray
            wi = reflect(normal, incident)
            pdf = P
            reflectance = RGBSpectrum(1.0, 1.0, 1.0) * R
        else: # transmission ray
            wi = refract(normal, incident, n1, n2)
            pdf = 1.0 - P
            T = 1.0 - R
            eta = (n1 * n1) / (n2 * n2)
            reflectance = RGBSpectrum(1.0, 1.0, 1.0) * T * eta

    ndotwi = normal.dot(wi)
    reflectance = reflectance * (1.0 / abs(ndotwi))
    return wi, pdf, reflectance


class MaterialMgrTest(unittest.TestCase):

    def atest_material_manager(self):
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
spec = sp.material_reflectance
        """
        pdf = FloatArg('pdf', 0.0)
        wi = Vec3Arg('wi', Vector3(0.0, 0.0, 0.0))
        spec = RGBArg('spec', RGBSpectrum(0.5, 0.5, 0.5))
        shader = Shader(code=code, args=[pdf, wi, spec])
        shader.compile(shaders=[mgr.sampling_shader])
        shader.prepare(runtimes)
        shader.execute()

        s = shader.get_value('pdf')
        print(s)
        s = shader.get_value('wi')
        print(s)
        s = shader.get_value('spec')
        print(s)
        normal = Vector3(0.1, 0.4, 0.66)
        normal.normalize()
        print(cos_hemisphere(r1=0.1, r2=0.06, normal=normal,e=1.0))

    def atest_material_glass(self):
        sam_mgr = SampledManager()
        register_rgb_shadepoint()

        runtimes = [Runtime()]
        mat = Material()
        mat.load('glass', sam_mgr, spectral=False)
        mat.set_value('ior', 1.5)

        mgr = MaterialManager()
        mgr.add('material1', mat)

        shaders = shaders_functions()
        for shader in shaders:
            shader.compile()
            shader.prepare(runtimes)

        mgr.compile_shaders(sam_mgr, spectral=False, shaders=shaders)
        mgr.prepare_shaders(runtimes)

        code = """
hp = HitPoint()
hp.normal = normal
sp = ShadePoint()
sp.wo = wo
material_sampling(hp, sp, 0)
pdf = sp.pdf
wi = sp.wi
spec = sp.material_reflectance
        """
        pdf = FloatArg('pdf', 0.0)
        wi = Vec3Arg('wi', Vector3(0.0, 0.0, 0.0))
        ww = Vector3(5.0, 1.0, 0.0)
        ww.normalize()
        wo = Vec3Arg('wo', ww)
        nn = Vector3(0.0, 1.0, 0.0)
        nn.normalize()
        normal = Vec3Arg('normal', nn)
        spec = RGBArg('spec', RGBSpectrum(0.5, 0.5, 0.5))

        shader = Shader(code=code, args=[pdf, wi, wo, normal, spec])
        shader.compile(shaders=[mgr.sampling_shader])
        shader.prepare(runtimes)

        shader.execute()

        s = shader.get_value('wi')
        print(s)
        s = shader.get_value('pdf')
        print(s)
        s = shader.get_value('spec')
        print(s)
        print('------------------------------')
        print('wo', ww)
        wi, pdf, ref = sampling_glass(1.5, ww, nn)
        print("wi", wi)
        print("pdf", pdf)
        print("ref", ref)
        ndotwi = abs(nn.dot(wi))
        print("ndotwi", ndotwi)

        tmp = ndotwi / pdf
        path_weight = ref * tmp
        print("path weight", path_weight)

if __name__ == "__main__":
    unittest.main()

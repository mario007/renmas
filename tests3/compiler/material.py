
import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float, Vec3, Vec2, Vec4
from renmas3.base import Vector2, Vector3, Vector4, Struct
from renmas3.base import register_user_type, create_user_type
from renmas3.base import RGBSpectrum, SampledSpectrum, Spectrum
from renmas3.base import ColorManager
from renmas3.renderer import SurfaceShader, Material, MaterialManager, ShadePoint

def next_direction():
    w = Vector3(2.3, 2.5, 8.8)
    w.normalize()

    #w = hitpoint.normal
    tv = Vector3(0.0034, 1.0, 0.0071)
    v = tv.cross(w)
    v.normalize()
    u = v.cross(w)

    pu = 0.6
    pv = 0.4
    pw = 0.8

    ndir = u * pu + v * pv + w * pw 
    ndir.normalize()

    pdf = w.dot(ndir) * 0.318309886

    return ndir, pdf
    

class Assign1Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_assign1(self):

        code = """
shadepoint.light_intensity = spectrum(0.25)

sample = sample_hemisphere()
sample = (0.6, 0.4, 0.8)
#w = hitpoint.normal 

w = (2.3, 2.5, 8.8)
w = normalize(w)
tv = (0.0034, 1.0, 0.0071)
v = cross(tv, w)
v = normalize(v)
u = cross(v, w)
ndir = u * sample[0] + v * sample[1] + w * sample[2]
shadepoint.wi = normalize(ndir)

shadepoint.pdf = dot(w, shadepoint.wi) * 0.318309886

        """
        props = {}
        col_mgr = ColorManager(spectral=True)
        brdf = SurfaceShader(code, props, col_mgr=col_mgr)
        mat = Material(bsdf=brdf)
        mgr = MaterialManager()
        mgr.add('blue_velvet', mat)
        runtime = Runtime()
        runtime2 = Runtime()
        runtimes = [runtime, runtime2]

        #bs.prepare([runtime])
        shader = mgr.prepare_bsdf('brdf', runtimes)
        #print (bs.shader._code)

        #bs.execute()
        sh = ShadePoint()
        code = """
hp = Hitpoint()
sp = Shadepoint()
brdf(hp, sp, 0)
spec = sp.light_intensity
wi = sp.wi
pdf = sp.pdf
        """
        wi = Vector3(2, 2, 2)
        spec = col_mgr.black()
        props = {'spec': spec, 'wi': wi, 'pdf': 0.0}
        bs = BasicShader(code, props, col_mgr=col_mgr)
        bs.prepare(runtimes, shaders=[shader])
        print (bs.shader._code)

        bs.execute()

        print(bs.shader.get_value('spec'))
        print(bs.shader.get_value('wi'))
        print(bs.shader.get_value('pdf'))
        print(next_direction())



if __name__ == "__main__":
    unittest.main()

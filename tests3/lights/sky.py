from tdasm import Runtime
from renmas3.base import ColorManager
from renmas3.renderer import LightManager 
from renmas3.renderer import SunSky
from renmas3.base import BasicShader, Vector3

col_mgr = ColorManager(spectral=False)
lgt_mgr = LightManager()

sun_sky = SunSky(col_mgr)

lgt_mgr.add('sunce', sun_sky)
runtimes = [Runtime()]
shader = lgt_mgr.prepare_illuminate('light_radiance', runtimes)

#light_radiance(hitpoint, shadepoint, 0)

code = """

hitpoint = Hitpoint()
shadepoint = Shadepoint()
shadepoint.wo = float3(-0.2, 0.3, 0.5)

light_radiance(hitpoint, shadepoint, 0)
spec = shadepoint.light_intensity
ret = hitpoint.t

"""
spec = col_mgr.create_spectrum((0.3, 0.2, 0.8))
props = {'spec':spec, 'ret':0.0}
bs = BasicShader(code=code, props=props, col_mgr=col_mgr)
bs.prepare(runtimes, [shader])
bs.execute()
print(bs.shader.get_value('spec'))

vec = Vector3(-0.2, 0.3, 0.5)
sun_sky.get_sky_spectrum(vec)


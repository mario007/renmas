import time
from renmas3.base import ImageBGRA
from renmas3.renderer import Renderer, Project
from renmas3.utils import blt_prgba_to_bgra
from renmas3.win32 import show_image_in_window

INTEGRATORS_CODE = """
sample = Sample()
ray = Ray()
hitpoint = Hitpoint()
shadepoint = Shadepoint()
ret = 1
nsamples = 0
color = spectrum(0.6)
color2 = spectrum(0.0)


while ret != 0:
    ret = generate_sample(sample)
    generate_ray(sample, ray)
    if ret == 0:
        break
    nsamples = nsamples + 1
    hit = isect(ray, hitpoint)
    if hit:
        light_illuminate(hitpoint, shadepoint, 0)
        brdf(hitpoint, shadepoint, hitpoint.material_idx)
        col = dot(hitpoint.normal, shadepoint.wi) * shadepoint.material_spectrum
        v = spectrum_to_rgb(col)
        add_sample(sample, v)
    else:
        v = spectrum_to_rgb(color2)
        add_sample(sample, v)
"""

ren = Renderer()
ren.parse_scene_file('scene1.txt')
#ren.open_project('scene1.proj')
ren.set_integrator_code(INTEGRATORS_CODE)

ren.prepare()
#print (ren._project.sampler.shader._code)

start = time.clock()
ren.render()
print(time.clock() - start)

ren.save_project('scene1.proj')
img2 = ren.output_image()
show_image_in_window(img2)


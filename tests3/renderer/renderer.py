import time
from renmas3.base import ImageBGRA
from renmas3.renderer import Renderer, Project
from renmas3.utils import blt_prgba_to_bgra
from renmas3.win32 import show_image_in_window

INTEGRATORS_CODE = """
sample = Sample()
ray = Ray()
hitpoint = Hitpoint()
ret = 1
nsamples = 0
color = (0.3, 0.0, 0.0)
color2 = (0.0, 0.3, 0.0)

while ret != 0:
    ret = generate_sample(sample)
    generate_ray(sample, ray)
    if ret == 0:
        break
    nsamples = nsamples + 1
    hit = isect(ray, hitpoint)
    if hit:
        add_sample(sample, color)
    else:
        add_sample(sample, color2)
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

#ren.save_project('scene1.proj')

img = ren._film._hdr_image
width, height = img.size()
img2 = ImageBGRA(width, height)

blt_prgba_to_bgra(img, img2)

show_image_in_window(img2)


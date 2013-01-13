import time
from tdasm import Runtime
from renmas3.base import ImageBGRA
from renmas3.renderer import Renderer, Project
from renmas3.utils import blt_prgba_to_bgra
from renmas3.win32 import show_image_in_window

INTEGRATORS_CODE = """
sample = Sample()
ray = Ray()
ret = 1
nsamples = 0
color = (0.12, 0.0, 0.0)
color2 = (0.32, 0.6, 0.0)
color3 = (0.52, 0.0, 0.0)
color4 = (0.88, 0.0, 0.0)
while ret != 0:
    ret = generate_sample(sample)
    generate_ray(sample, ray)
    #generate_ray(ray, sample) FIXME -- trow execption somehow
    if ret == 0:
        break
    nsamples = nsamples + 1
    if sample.iy > 20:
        add_sample(sample, color)
    else:
        add_sample(sample, color2)
"""

ren = Renderer()
ren.parse_scene_file('scene1.txt')
ren.set_integrator_code(INTEGRATORS_CODE)

ren.prepare()

start = time.clock()
ren.render()
print(time.clock() - start)


img = ren._film._hdr_image
width, height = img.size()
img2 = ImageBGRA(width, height)

blt_prgba_to_bgra(img, img2)

show_image_in_window(img2)


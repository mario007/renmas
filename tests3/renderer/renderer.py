import time
from renmas3.base import ImageBGRA, save_image
from renmas3.renderer import Renderer, Project
from renmas3.utils import blt_prgba_to_bgra
from renmas3.win32 import show_image_in_window

ren = Renderer()
#ren.parse_scene_file('../scenes/sphere1.txt')
#ren.parse_scene_file('../scenes/sphere_env.txt')
#ren.parse_scene_file('../scenes/cornel1.txt')
#ren.parse_scene_file('../scenes/cornel2.txt')
#ren.parse_scene_file('../scenes/cornel3.txt')

#ren.parse_scene_file('../scenes/cornel4.txt')
#ren.parse_scene_file('../scenes/cube.txt')
#ren.parse_scene_file('../scenes/dragon.txt')
#ren.parse_scene_file('../scenes/dielectric.txt')
ren.parse_scene_file('../scenes/dielectric2.txt')

#ren.parse_scene_file('F:/ray_tracing_scenes/mitsuba_material/scene.txt')
#ren.parse_scene_file('F:/ray_tracing_scenes/san-miguel/scene.txt')
#ren.open_project('scene1.proj')

start = time.clock()
ren.prepare()
end = time.clock() - start
print ("Prezivili pripremu. Priprema trajala %f" % end)

start = time.clock()
ret = False
frame_pass = 0
while not ret:
    ret = ren.render()
    frame_pass += 1
    print("Frame number %i" % frame_pass)
print(time.clock() - start)

ren.save_project('scene1.proj')
img2 = ren.output_image()
show_image_in_window(img2)

save_image('picture.png', img2)

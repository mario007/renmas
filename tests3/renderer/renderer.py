import time
from renmas3.base import ImageBGRA, save_image
from renmas3.renderer import Renderer, Project
from renmas3.utils import blt_prgba_to_bgra
from renmas3.win32 import show_image_in_window

ren = Renderer()
#ren.parse_scene_file('../scenes/sphere1.txt')
#ren.parse_scene_file('../scenes/cornel1.txt')
#ren.parse_scene_file('../scenes/cornel2.txt')
#ren.parse_scene_file('../scenes/cornel3.txt')
ren.parse_scene_file('../scenes/cornel4.txt')

#ren.open_project('scene1.proj')

ren.prepare()

start = time.clock()
ret = False
while not ret:
    ret = ren.render()
print(time.clock() - start)

ren.save_project('scene1.proj')
img2 = ren.output_image()
show_image_in_window(img2)

save_image('picture.tga', img2)


import time
import random
import winlib
import renmas2
import renmas2.core
import renmas2.shapes

rnd = renmas2.Renderer()

blitter = renmas2.core.Blitter()
def blt_float_img_to_window(x, y, img, win):
    da, dpitch = win.get_addr()
    dw, dh = win.get_size()
    sa, spitch = img.get_addr()
    sw, sh = img.get_size()
    blitter.blt_floatTorgba(da, x, y, dw, dh, dpitch, sa, 0, 0, sw, sh, spitch)

def random_spheres(renderer, n):
    for i in range(n):
        center = renmas2.core.Vector3(0.0, 0.0, 0.0)
        radius = random.random() * 1.5 
        sph = renmas2.shapes.Sphere(center, radius, 0)
        renderer.add('sphere'+str(i), sph)

random_spheres(rnd, 1)
rnd.prepare()

#start = time.clock()
#while True:
#    ret = rnd.render()
#    if not ret: break

#end = time.clock()
#print(end-start)

def render_scene():
    ret = rnd.render()
    if not ret: return 
    blt_float_img_to_window(0, 0, rnd._film.image, win)

win = renmas2.core.MainWindow(600, 400, "Test")
blt_float_img_to_window(0, 0, rnd._film.image, win)
win.redraw()
win.render_handler(render_scene)
winlib.MainLoop()


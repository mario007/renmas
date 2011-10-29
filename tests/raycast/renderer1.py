
import renmas
import winlib
import renmas.gui 
import time
import concurrent.futures

blitter = renmas.gui.Blitter()
def blt_float_img_to_window(x, y, img, win):
    da, dpitch = win.get_addr()
    dw, dh = win.get_size()
    sa, spitch = img.get_addr()
    sw, sh = img.get_size()
    blitter.blt_floatTorgba(da, x, y, dw, dh, dpitch, sa, 0, 0, sw, sh, spitch)

renderer = renmas.renderer # renderer
ren = renmas.ren #high level interface

l_props = {"type":"point", "name": "light1", "position":(5,5.5,5.2), "spectrum":(1.99,1.99,1.99)}
ren.create_light(l_props)
l_props = {"type":"point", "name": "light2", "position":(-100, 10, -30), "spectrum":(1.99,0.0,1.99)}
ren.create_light(l_props)
l_props = {"type":"point", "name": "light3", "position":(-440, 160, 28), "spectrum":(4.99,4.99,4.99)}
ren.create_light(l_props)

m_props = {"name": "m1", "sampling":"hemisphere_cos"}
m = ren.create_material(m_props)
m_props = {"type":"lambertian", "R":(0.342, 0.155, 0.115)} # left wall- red wall
ren.add_brdf("m1", m_props)
m_props = {"type":"phong", "R":(0.2, 0.2, 0.2), "e": 12.2, "k":0.3}
ren.add_brdf("m1", m_props)

sh_props = {"type":"sphere", "position":(0.0, 0.0, 0.0), "radius":3.0, "material":"m1"}
#s = ren.create_shape(sh_props)

#sh_props = {"type":"mesh", "resource":["dragon_vrip_res4.ply"], "material":"m1" , "translate":(0.2,-1.65,0.0), "scale":(48, 48, 48)}
sh_props = {"type":"mesh", "resource":["Blade.obj"], "material":"m1" }
#s = ren.create_shape(sh_props)

sh_props = {"type":"mesh", "resource":["Handle.obj"], "material":"m1" }
#s = ren.create_shape(sh_props)

sh_props = {"type":"mesh", "resource":["butt.obj"], "material":"m1" }
#s = ren.create_shape(sh_props)

sh_props = {"type":"mesh", "resource":["Old_Key.obj"], "material":"m1" }
s = ren.create_shape(sh_props)

renderer.set_resolution(800, 800)
renderer.set_samples_per_pixel(1)
renderer.set_pixel_size(0.5)

#renderer.set_rendering_algorithm("pathtracer_py")

renderer.prepare()

duration = 0.0
def render_scene():

    start = time.clock()
    ret = renderer.render()
    if ret is True: return
    end = time.clock()
    global duration
    duration = duration + (end - start)
    print(duration)

    picture = renderer.get_picture(None)
    blt_float_img_to_window(0, 0, picture, win)

win = renmas.gui.MainWindow(600, 400, "Test")

blt_float_img_to_window(0, 0, renderer.get_picture(None), win)
win.redraw()
win.render_handler(render_scene)
winlib.MainLoop()



import time
import random
import winlib
import renmas2
import renmas2.core
import renmas2.shapes

renderer = renmas2.Renderer()
irender = renmas2.IRender(renderer)
factory = renmas2.Factory()

blitter = renmas2.core.Blitter()
def blt_float_img_to_window(x, y, img, win):
    da, dpitch = win.get_addr()
    dw, dh = win.get_size()
    sa, spitch = img.get_addr()
    sw, sh = img.get_size()
    blitter.blt_floatTorgba(da, x, y, dw, dh, dpitch, sa, 0, 0, sw, sh, spitch)

#irender.set_props("camera", "eye", "5.0,6.3,9.6")
#renderer.set_pixel_size(1.5)
#renderer.resolution(400, 300)
#irender.set_props('misc', 'pixel_size', '0.5')
#print(irender.get_props('misc', 'pixel_size'))
#irender.set_props('misc', 'resolution', '400,300')
#print (irender.get_props('misc', 'resolution'))
irender.set_props('misc', 'spp', '1')
print (irender.get_props('misc', 'spectral'))
print (irender.get_props('misc', 'pixel_size'))

irender.set_props('misc', 'threads', '4')
#filename = 'I:\\GitRENMAS\\scenes\\sphere1.py'
filename = 'I:\\GitRENMAS\\scenes\\cornel2.py'
exec(compile(open(filename).read(), filename, 'exec'), dict(locals()), dict(globals()))
#irender.set_props('misc', 'pixel_size', '1.4')
#print (irender.get_props('misc', 'pixel_size'))
#print (irender.get_props('light_spectrum', 'light1'))
#irender.set_props('misc', 'spectral', 'True')

#irender.set_props("light_intesity", "light1", "380,1.5")
#irender.set_props("light_intesity", "light1", "RED,1.5")
for l  in renderer.shader.light_names():
    print(l)
#renderer.spectral_rendering = True
renderer.prepare()
#print(renderer.get_log())
print(irender.get_props("misc", "log"))

#start = time.clock()
#while True:
#    ret = rnd.render()
#    if not ret: break

#end = time.clock()
#print(end-start)

ret = True
def render_scene():
    start = time.clock()
    global ret
    if not ret: return 
    while True:
        ret = renderer.render()
        if not ret: break
    #if not ret: return 
    end = time.clock()
    print (end-start)
    #renderer._film.tone_map()
    blt_float_img_to_window(0, 0, renderer._film.image, win)

win = renmas2.core.MainWindow(600, 400, "Test")
blt_float_img_to_window(0, 0, renderer._film.image, win)
win.redraw()
win.render_handler(render_scene)
winlib.MainLoop()


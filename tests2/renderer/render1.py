
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

def blt_framebuffer_to_window(x, y, img, win):
    da, dpitch = win.get_addr()
    dw, dh = win.get_size()
    sa, spitch = img.get_addr()
    sw, sh = img.get_size()
    blitter.blt_rgba(da, x, y, dw, dh, dpitch, sa, 0, 0, sw, sh, spitch)

#irender.set_props("camera", "eye", "5.0,6.3,9.6")
#renderer.set_pixel_size(1.5)
#renderer.resolution(400, 300)
#irender.set_props('misc', 'pixel_size', '0.5')
#print(irender.get_props('misc', 'pixel_size'))
#irender.set_props('misc', 'resolution', '400,300')
#print (irender.get_props('misc', 'resolution'))
#irender.set_props('misc', 'spp', '1')
print (irender.get_props('misc', 'spectral'))
print (irender.get_props('misc', 'pixel_size'))

#irender.set_props('misc', 'threads', '1')
filename = 'I:\\GitRENMAS\\scenes\\sphere3.py'
filename = 'I:\\GitRENMAS\\scenes\\troll.py'
#filename = 'I:\\GitRENMAS\\scenes\\cornel2.py'
#filename = 'I:\\GitRENMAS\\scenes\\cube_mesh.py'
#filename = 'I:\\GitRENMAS\\scenes\\lux_ball.py'
#filename = 'I:\\GitRENMAS\\scenes\\cube.py'
#filename = 'I:\\GitRENMAS\\scenes\\random_spheres.py'
#filename = 'I:\\GitRENMAS\\scenes\\mini_moris.py'
exec(compile(open(filename).read(), filename, 'exec'), dict(locals()), dict(globals()))
#irender.set_props('misc', 'pixel_size', '1.4')
#print (irender.get_props('misc', 'pixel_size'))
#print (irender.get_props('light_spectrum', 'light1'))
#irender.set_props('misc', 'spectral', 'True')

irender.set_props('misc', 'selected_operator',  "Reinhard")
print("Operator", irender.get_props("misc", "selected_operator"))
print("Tonemapping", irender.get_props("misc", "tone_mapping"))

#print(irender.get_props("misc", "shapes"))
#print(irender.get_props("misc", "materials"))
#print ("Materials for shapes")
#print(irender.get_props("material_name", "Ceiling"))
#print(irender.get_props("material_name", "Left_wall"))
#print(irender.set_props("material_assign", "Left_wall", "default"))
#print(irender.get_props("material_name", "Left_wall"))

#irender.set_props("light_intesity", "light1", "380,1.5")
#irender.set_props("light_intesity", "light1", "RED,1.5")
for l  in renderer.shader.light_names():
    print(l)
#renderer.spectral_rendering = True
renderer.prepare()
#print(renderer.get_log())
#print(irender.get_props("misc", "log"))

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
    print ("Rendering took:", end-start)
    
    renderer.tone_map()
    blt_framebuffer_to_window(0, 0, renderer._film.frame_buffer, win)

win = renmas2.core.MainWindow(600, 400, "Test")
blt_float_img_to_window(0, 0, renderer._film.image, win)
win.redraw()
win.render_handler(render_scene)
winlib.MainLoop()


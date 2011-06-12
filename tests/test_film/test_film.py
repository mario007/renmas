
import renmas.gui
import winlib
import renmas.core
import renmas.samplers
import renmas.shapes
from tdasm import Runtime

blitter = renmas.gui.Blitter()
def blt_float_img_to_window(x, y, img, win):
    da, dpitch = win.get_addr()
    dw, dh = win.get_size()
    sa, spitch = img.get_addr()
    sw, sh = img.get_size()
    blitter.blt_floatTorgba(da, x, y, dw, dh, dpitch, sa, 0, 0, sw, sh, spitch)

def draw_film(film):
    sample = renmas.samplers.Sample()
    hp = renmas.shapes.HitPoint()
    
    hp.spectrum = renmas.core.Spectrum(0.0, 0.0, 0.99)

    for x in range(film.width):
        for y in range(film.height):
            for i in range(film.numsamples()):
                sample.ix = x
                sample.iy = y
                film.add_sample(sample, hp)

def draw_film_asm(film, runtime, ds):
    hp = renmas.shapes.HitPoint()
    
    hp.spectrum = renmas.core.Spectrum(0.00, 0.90, 0.00)
    s = hp.spectrum
    ds["hp1.spectrum"] = (s.r, s.g, s.b, 0.0)

    for x in range(film.width):
        for y in range(film.height):
            for i in range(film.numsamples()):
                ds["sp1.ix"] = x 
                ds["sp1.iy"] = y 
                runtime.run("test")

film = renmas.core.Film(100, 100, 1)
#draw_film(film)

asm_structs = renmas.utils.structs("hitpoint", "sample")
ASM = """
    #DATA
"""
ASM += asm_structs + """
    hitpoint hp1
    sample sp1

    #CODE
    mov eax, hp1
    mov ebx, sp1 
    call add_sample

    #END
"""

runtime = Runtime()
film.add_sample_asm(runtime, "add_sample")
asm = renmas.utils.get_asm()
mc = asm.assemble(ASM) 
ds = runtime.load("test", mc)

draw_film_asm(film, runtime, ds)

win = renmas.gui.MainWindow(500, 500, "Test")

blt_float_img_to_window(10, 10, film.image, win)

win.redraw()
winlib.MainLoop()


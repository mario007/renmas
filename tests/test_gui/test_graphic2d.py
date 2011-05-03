
import winlib
import renmas.gui 

#BGRA Format - Little endian
def draw_lines(g):
    g.set_color(0xFF0000FF) #blue
    for x in range(50):
        g.set_pixel(x, 40)

    g.set_color(0xFF00FF00) #green
    for x in range(75):
        g.set_pixel(x, 80)

    g.set_color(0xFFFF0000) #red
    for x in range(75):
        g.set_pixel(x, 120)


win = renmas.gui.MainWindow(500, 500, "Test")
addr, pitch = win.get_addr()
g = renmas.gui.Graphic2D(200, 200, pitch, addr)
draw_lines(g)

win.redraw()
winlib.MainLoop()


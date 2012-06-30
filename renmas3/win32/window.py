import os
import time
import winlib

def main_loop():
    winlib.MainLoop()

class Window:
    def __init__(self, width, height, title="Uninitiliazed"):
        self.fb = winlib.Window(title, width, height, self) 
        self.background = (0, 0, 0)

    def destroy(self):
        self.fb.destroy()

    def char_pressed(self, char):
        if char > 127: return
        if char == 98: # 98 = b
            self.real_time(True)
        if char == 115:  # 115 = s
            self.real_time(False)

    def address_info(self):
        w, h = self.fb.get_size()
        return (self.fb.pixels(), w * 4)

    def size(self): #return size of the frame buffer
        return self.fb.get_size()

    def real_time(self, state):
        if state:
            winlib.RealTime(1, self)
        else:
            winlib.RealTime(0, self)

    #events must have exact names like l_mouse_down because
    #winlib extensions count on this 
    def l_mouse_down(self, px, py):
        pass

    def l_mouse_up(self, px, py):
        pass

    def mouse_move(self, px, py, key):
        pass

    def render(self):
        rez = self.rnd_handler()
        self.redraw()
        if rez is None: self.real_time(False)

    def render_handler(self, handler):
        self.rnd_handler = handler

    def clear_buffer(self, r, g, b):
        self.fb.clear_buffer(r, g, b)

    def redraw_all(self): #redraw self and child windows
        r, g, b = self.background
        self.fb.clear_buffer(r, g, b) #background
        self.redraw()

    def redraw(self):
        self.fb.redraw()


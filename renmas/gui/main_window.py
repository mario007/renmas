import os
import time
import winlib

class MainWindow(object):
    def __init__(self, width, height, title="Uninitiliazed"):
        self.width = width
        self.height = height

        self.fb = winlib.Window(title, width, height, self) 

        self.controls = {} #child controls
        self.enter_control = None # for regulating mouse_enter and mouse_leave events
        self.focus = None # for regulating got_focus and lost_focus events
        self.background = (0, 0, 0)
        #self.clear_buffer(0,255,0)
        self.menubar = None # controling menu bar
        self.menu = None # for removing menu

        #parameters for rendering
        self.rendering = False
        self.npix = 0


    def set_menubar(self, menubar):
        self.menubar = menubar
        self.add_control(menubar, (0, 0))

    def set_menu(self, menu, pos):
        m = None
        if self.menu is not None:
            if self.menu == menu:
                return
            else:
                m = self.menu
        self.menu = menu
        self.add_control(menu, pos)
        if m is not None: 
            self.remove_control(m)


    def destroy(self):
        #winlib.Quit()
        self.fb.destroy()

    def add_control(self, control, pos):#FIXME if we have two same controls 
        self.controls[control] = pos
        control.render(pos)

    def set_focus(self, con):
        if self.focus is not None:
            self.focus.lost_focus()
        con.got_focus()
        self.focus = con

    def get_position(self, con):
        return self.controls[con]

    def get_control(self, con):
        try:
            c = self.controls[con]
            return con
        except:
            return None

    def remove_control(self, control):
        try:
            con = self.controls[control]
            if self.focus == control: self.focus = None
            del self.controls[control]
            self.redraw_all()
            return control
        except:
            return None 

    def char_pressed(self, char):
        if char > 127: return
        if self.focus is not None:
            self.focus.char_pressed(char)

    def get_addr(self): #get address of frame buffer
        #return winlib.GetAddress()
        w, h = self.fb.get_size()
        return self.fb.pixels(), w * 4

    def size_change(self, width, height):
        self.width = width
        self.height = height

    def real_time(self, state):
        if state:
            winlib.RealTime(1, self)
        else:
            winlib.RealTime(0, self)

    #events must have exact names like l_mouse_down because
    #winlib extensions count on this 
    def l_mouse_down(self, px, py):
        cons = self._pt_in_con(px, py)
        if len(cons) == 0:
            if self.focus is not None:
                self.focus.lost_focus()
                self.focus = None

        #handling of menu
        if self.menu is not None:
            if self.menu in cons:
                pos = self.controls[self.menu]
                self.menu.left_mouse_down(px - pos[0], py - pos[1])
                self.remove_control(self.menu)
                self.menu = None
                return 
            else: 
                if self.menubar is not None and self.menubar not in cons:
                    self.remove_control(self.menu)
                    self.menu = None

        for con in cons:
            pos = self.controls[con] 
            con.left_mouse_down(px - pos[0], py - pos[1])
            if self.focus is not None and self.focus != con:
                self.focus.lost_focus()
                self.focus = None
            if self.focus is None:
                con.got_focus()
                self.focus = con

    def _pt_in_con(self, px, py): #return list of control that contains specified point
        controls = []
        for con, pos in self.controls.items():
            x, y = pos
            width, height = con.get_size()
            if px >= x and px <= x + width and py >= y and py <= y + height:
                controls.append(con)
        return controls


    def l_mouse_up(self, px, py):
        for con in self._pt_in_con(px, py):
            pos = self.controls[con]
            con.left_mouse_up(px - pos[0], py - pos[1])

    def mouse_move(self, px, py, key):
        cons = self._pt_in_con(px, py)
        if len(cons) == 0:
            if self.enter_control is not None:
                self.enter_control.mouse_leave()
                self.enter_control = None

        for con in cons: #be carefull if control doesnt't exist this will break! FIXME
            pos = self.controls[con]
            con.mouse_move(px - pos[0], py - pos[1])
            if self.enter_control is not None and self.enter_control != con:
                self.enter_control.mouse_leave()
                self.enter_control = None

            if self.enter_control is None:
                con.mouse_enter()
                self.enter_control = con

    def render(self):
        if self.rendering:
            if self.rnd.is_finished():
                self.stop_rendering()
                self.rnd_control.refresh()
                return
            self.render_func(self.rnd)
            self.npix += 1
            if self.npix == 4096:
                self.npix = 0
                self.rnd_control.refresh()

    def set_rendering(self, func, rnd, rnd_control):
        self.render_func = func
        self.rnd = rnd
        self.rnd_control = rnd_control

    def start_rendering(self):
        if self.rendering: return
        self.start_time = time.clock()
        self.rendering = True
        self.real_time(True)

    def stop_rendering(self):
        end = time.clock()
        print("Rendering time = ", end - self.start_time)
        self.rendering = False
        self.real_time(False)


    def clear_buffer(self, r, g, b):
        self.fb.clear_buffer(r, g, b)

    def redraw_all(self): #redraw self and child windows
        r, g, b = self.background
        self.fb.clear_buffer(r, g, b) #background
        for con, pos in self.controls.items():
            con.render(pos)
        self.redraw()

    def refresh_menubar(self):
        if self.menubar is not None:
            self.menubar.render((0,0))
            self.redraw()

    def refresh_control(self, control):
        pos = self.controls[control]
        control.render(pos)
        if self.menu is not None:
            self.menu.render(self.controls[self.menu])
        self.redraw()

    def redraw(self):
        self.fb.redraw()

    def main_loop(self):
        self.fb.redraw()
        winlib.MainLoop()


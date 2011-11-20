

class Integrator:
    def __init__(self, renderer):
        self._renderer = renderer
        self._asm = False

    def asm(self, flag):
        self._asm = bool(flag)

    def render(self, tile):
        if self._asm:
            self.render_asm(tile)
        else:
            #self.render_asm(tile)
            self.render_py(tile)

    def render_py(self, tile):
        raise NotImplementedError()

    def render_asm(self, tile):
        raise NotImplementedError()
    
    def prepare(self):
        raise NotImplementedError()


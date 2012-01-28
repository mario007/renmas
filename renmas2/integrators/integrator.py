

class Integrator:
    def __init__(self, renderer):
        self._renderer = renderer

    def render(self, tile):
        if self._renderer.asm:
            self.render_asm(tile)
        else:
            self.render_py(tile)

    def render_py(self, tile):
        raise NotImplementedError()

    def render_asm(self, tile):
        raise NotImplementedError()
    
    def prepare(self):
        raise NotImplementedError()


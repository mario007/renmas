
from .factory import Factory

class IRender:
    def __init__(self, renderer):
        self._renderer = renderer
        self._factory = Factory()

    def add_shape(self, **kw):
        shape = self._factory.create_shape(**kw)
        name = kw.get("name", None)
        if name is not None:
            self._renderer.add(name, shape)
        #TODO assign material
        

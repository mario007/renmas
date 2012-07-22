
from .col_mgr import ColorManager
from .logger import log

class Renderer:
    def __init__(self):

        self._ready = False
        self._default_values()
        self._default_objects()

    def _default_values(self):
        self._width =  300 
        self._height = 300 
        self._spp = 1 
        self._threads = 1 
        self._max_samples = 100000 #max samples in tile
        self._pixel_size = 1.0
        self._default_material = "default" #name of default material
        self._asm = False 
        self._tone_mapping = True 
        self._current_pass = 0

    def _default_objects(self):
        self._color_manager = ColorManager()
        pass

    @property
    def macro_call(self):
        return self._color_manager.macro_call

    @property
    def assembler(self):
        return self._color_manager.assembler

    @property
    def color_mgr(self):
        return self._color_manager


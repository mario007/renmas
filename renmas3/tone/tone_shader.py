from tdasm import Runtime
from ..base import Vector3, create_shader, arg_map, arg_list, Vec3, Float
from ..base import Tile2D, ImagePRGBA
from .props import ImageProps, calc_img_props

class TmoShader:
    def __init__(self, py_code=None, code=None, props=None):

        self._py_code = py_code
        self._code = code
        self._props = props
        if props is None:
            self._props = []

        self._shader = None
        self._runtimes = None

    @property
    def shader(self):
        return self._shader

    def prepare(self, nthreads=1):
        if nthreads > 32:
            nthreads = 32
        self._runtimes =  [Runtime() for i in range(nthreads)]

        props = [('img_props', ImageProps), ('tile', Tile2D),
            ('in_img', ImagePRGBA), ('out_img', ImagePRGBA)]
        for p in self._props:
            props.append(p)

        _arg_map = arg_map(props)
        self._shader = create_shader("tmo_shader", self._code, _arg_map)
        self._shader.prepare(self._runtimes)
        #print(self._shader._code)

    def tmo(self, in_img, out_img):
        if self._shader is None:
            return
        width, height = in_img.size()
        props = calc_img_props(in_img)
        tile = Tile2D(0, 0, width, height)
        #TODO if we have only one thread we dont have to split
        tile.split(len(self._runtimes))
        for idx, t in enumerate(tile.tiles):
            self._shader.set_value('tile', t, idx_thread=idx)
            self._shader.set_value('img_props', props, idx_thread=idx)
            self._shader.set_value('in_img', in_img, idx_thread=idx)
            self._shader.set_value('out_img', out_img, idx_thread=idx)
            for p in self._props:
                self._shader.set_value(p.name, p.value, idx_thread=idx)

        self._shader.execute(nthreads=len(tile.tiles))

    def tmo_py(self, in_img, out_img):
        props = calc_img_props(in_img)
        attrs = {'img_props':props}
        for p in self._props:
            attrs[p.name] = p.value
        return self._py_code(attrs, in_img, out_img)


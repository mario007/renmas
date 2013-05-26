
from ..base import Ray
from ..base import VertexBuffer, TriangleBuffer
from ..macros import create_assembler
from .hit import HitPoint
from .base_mesh import BaseMesh
from .grid_mesh import GridMesh

class FlatMesh(BaseMesh):
    def __init__(self, vb, tb, material_idx=0):
        super(FlatMesh, self).__init__()

        if not isinstance(vb, VertexBuffer):
            raise ValueError("Wrong vertex buffer", vb)
        if not isinstance(tb, TriangleBuffer):
            raise ValueError("Wrong triangle buffer", tb)

        self._vb = vb
        self._tb = tb
        self.material_idx = material_idx

        self._grid = GridMesh()
        #start = time.clock()
        self._grid.setup(self)
        #print(time.clock() - start)
        #print(self._grid._show_info())

    @property
    def vb(self):
        return self._vb

    @property
    def tb(self):
        return self._tb


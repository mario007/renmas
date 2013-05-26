
from renmas3.base import VertexBuffer, TriangleBuffer
from renmas3.shapes import load_meshes
from renmas3.shapes import FlatMesh

def create_mesh(desc):
    vb = desc.vb
    tb = desc.tb
    if isinstance(vb, VertexBuffer) and isinstance(tb, TriangleBuffer):
        mesh = FlatMesh(vb, tb)
    else:
        raise ValueError("Buffer combination is not yet supported!")
    return mesh

mdescs = load_meshes('F:/Ply_files/cube.ply')
#mdescs = load_meshes('F:/Ply_files/dragon_vrip.ply')
for desc in mdescs:
    mesh = create_mesh(desc)


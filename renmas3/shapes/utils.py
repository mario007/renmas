
import os.path
from renmas3.base import VertexBuffer, TriangleBuffer, Vector3
from renmas3.base import VertexNBuffer, VertexNUVBuffer, VertexUVBuffer
from .triangle import Triangle
from .load_meshes import load_meshes
from .flat_mesh import FlatMesh
from .smooth_mesh import SmoothMesh
from .smooth_uv_mesh import SmoothUVMesh
from .flat_uv_mesh import FlatUVMesh

def create_mesh(desc, performanse=True):
    vb = desc.vb
    tb = desc.tb
    if isinstance(vb, VertexBuffer) and isinstance(tb, TriangleBuffer):
        mesh = FlatMesh(vb, tb)
    elif isinstance(vb, VertexNBuffer) and isinstance(tb, TriangleBuffer):
        mesh = SmoothMesh(vb, tb)
    elif isinstance(vb, VertexNUVBuffer) and isinstance(tb, TriangleBuffer):
        mesh = SmoothUVMesh(vb, tb)
    elif isinstance(vb, VertexUVBuffer) and isinstance(tb, TriangleBuffer):
        mesh = FlatUVMesh(vb, tb)
    else:
        raise ValueError("Buffer combination is not yet supported!")
    return mesh

def fetch_triangle(mesh, index):
    v0, v1, v2 = mesh.get_indices(index)
    p0 = mesh.get_point(v0)
    p0 = Vector3(p0[0], p0[1], p0[2])
    p1 = mesh.get_point(v1)
    p1 = Vector3(p1[0], p1[1], p1[2])
    p2 = mesh.get_point(v2)
    p2 = Vector3(p2[0], p2[1], p2[2])
    if mesh.has_normals():
        n0 = mesh.get_normal(v0)
        n0 = Vector3(n0[0], n0[1], n0[2])
        n1 = mesh.get_normal(v1)
        n1 = Vector3(n1[0], n1[1], n1[2])
        n2 = mesh.get_normal(v2)
        n2 = Vector3(n2[0], n2[1], n2[2])
    else:
        n0 = n1 = n2 = None
    if mesh.has_uv():
        uv0 = mesh.get_uv(v0)
        uv1 = mesh.get_uv(v1)
        uv2 = mesh.get_uv(v2)
        tu0 = uv0[0]
        tv0 = uv0[1]
        tu1 = uv1[0]
        tv1 = uv1[1]
        tu2 = uv2[0]
        tv2 = uv2[1]
    else:
        tu0 = tv0 = tu1 = tv1 = tu2 = tv2 = None
    tri = Triangle(p0, p1, p2, mesh.material_idx, n0=n0, n1=n1, n2=n2,
            tu0=tu0, tv0=tv0, tu1=tu1, tv1=tv1, tu2=tu2, tv2=tv2)
    #tri = Triangle(p0, p1, p2, mesh.material_idx, n0=n0, n1=n1, n2=n2)
    return tri

def load_meshes_from_file(filename, performanse=True):
    if not os.path.isfile(filename):
        raise ValueError("File %s doesn't exist!" % filename)

    meshes = {}
    mdescs = load_meshes(filename)
    for desc in mdescs:
        mesh = create_mesh(desc, performanse)
        if desc.name is None:
            meshes['mesh' + str(id(mesh))] = mesh
        else:
            meshes[desc.name] = mesh
    return meshes


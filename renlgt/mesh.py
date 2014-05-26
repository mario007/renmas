
import os.path
from random import random
from sdl import Vector3, register_struct, Ray, Shader, PointerArg,\
    IntArg, StructArgPtr, FloatArg, Vec3Arg, StructArg
from .buffers import VertexBuffer, VertexNBuffer, VertexUVBuffer,\
    VertexNUVBuffer, TriangleBuffer
from .obj import Obj
from .ply import Ply
from .bbox import BBox
from .grid_mesh import GridMesh
from .shape import Shape, DependencyShader
from .hitpoint import HitPoint
from .shader_lib import ray_triangle_isect_shader
from .save import save_mesh_data
from .tri_box_overlap import tri_box_overlap
from .shadepoint import ShadePoint


def load_meshes(filename):
    name, ext = os.path.splitext(filename)
    if ext == "":
        return None
    if ext == '.ply':
        l = Ply()
    elif ext == '.obj':
        l = Obj()
    else:
        return None
    return l.load(filename)


class BaseMesh(Shape):
    def __init__(self):
        super(Shape, self).__init__()
        self._grid = None

    def prepare(self, performanse=False):
        self._grid = GridMesh()
        self._grid.setup(self, performanse=performanse)

    @property
    def bbox_min(self):
        if self._grid is None:
            return Vector3(0.0, 0.0, 0.0)
        g = self._grid
        return Vector3(g.bbox.x0, g.bbox.y0, g.bbox.z0)

    @property
    def bbox_max(self):
        if self._grid is None:
            return Vector3(0.0, 0.0, 0.0)
        g = self._grid
        return Vector3(g.bbox.x1, g.bbox.y1, g.bbox.z1)

    @property
    def nx(self):
        if self._grid is None:
            return 0
        return self._grid.nx

    @property
    def ny(self):
        if self._grid is None:
            return 0
        return self._grid.ny

    @property
    def nz(self):
        if self._grid is None:
            return 0
        return self._grid.nz

    @property
    def cells(self):
        if self._grid is None:
            return 0
        return self._grid.asm_cells.ptr()

    @property
    def lin_arrays(self):
        if self._grid is None:
            return 0
        return self._grid.lin_array.ptr()

    @classmethod
    def isect_shader(cls, shader_name):

        dep_shader = cls.isect_triangles_shader()
        code = GridMesh.isect_shader_code(dep_shader.shader.name)

        args = []
        func_args = [StructArgPtr('ray', Ray.factory()),
                     StructArgPtr('mesh', cls.empty_mesh()),
                     StructArgPtr('hitpoint', HitPoint.factory()),
                     FloatArg('min_dist', 0.0)]

        shader = Shader(code=code, args=args, name=shader_name,
                        func_args=func_args, is_func=True)
        return DependencyShader(shader, [dep_shader])

    @classmethod
    def isect_b_shader(cls, shader_name):
        dep_shader = cls.isect_triangles_b_shader()
        code = GridMesh.isect_shader_b_code(dep_shader.shader.name)

        args = []
        func_args = [StructArgPtr('ray', Ray.factory()),
                     StructArgPtr('mesh', cls.empty_mesh()),
                     FloatArg('min_dist', 0.0)]

        shader = Shader(code=code, args=args, name=shader_name,
                        func_args=func_args, is_func=True)
        return DependencyShader(shader, [dep_shader])

    def isect_triangles(self, ray, triangles, min_dist=999999.0):
        hit_point = False 
        for idx in triangles:
            hit = self.ray_triangle(ray, idx, min_dist) 
            if hit is False:
                continue
            if hit.t < min_dist:
                min_dist = hit.t
                hit_point = hit
        return hit_point

    def isect(self, ray, min_dist=999999.0):  # ray dir. must be normalized
        return self._grid.isect(ray, min_dist)

    def isect_b(self, ray, min_dist=99999.0):  # ray dir. must be normalized
        hp = self._grid.isect(ray, min_dist)
        if hp:
            return True
        return False

    @classmethod
    def empty_mesh(cls):
        raise NotImplementedError()

    def ntriangles(self):
        raise NotImplementedError()

    def bbox(self):
        raise NotImplementedError()

    def bbox_triangle(self, idx):
        raise NotImplementedError()

    def ray_triangle(self, ray, idx, min_dist = 999999.0):
        raise NotImplementedError()

class FlatMesh(BaseMesh):
    def __init__(self, vb, tb, mat_idx=0, light_id=-1):
        super(FlatMesh, self).__init__()

        if not isinstance(vb, VertexBuffer):
            raise ValueError("Wrong vertex buffer", vb)
        if not isinstance(tb, TriangleBuffer):
            raise ValueError("Wrong triangle buffer", tb)

        self._vb = vb
        self._tb = tb
        self.mat_idx = mat_idx
        self.light_id = light_id

        self._min_p = None
        self._max_p = None

    @classmethod
    def empty_mesh(cls):
        return FlatMesh(VertexBuffer(), TriangleBuffer(), mat_idx=0)

    def bbox(self):
        if self._min_p is None or self._max_p is None:
            min_p, max_p = self._vb.bbox()
            self._min_p = min_p
            self._max_p = max_p

        min_p = self._min_p
        max_p = self._max_p
        p0 = Vector3(min_p[0], min_p[1], min_p[2])
        p1 = Vector3(max_p[0], max_p[1], max_p[2])
        return BBox(p0, p1)

    def translate(self, dx, dy, dz):
        self._vb.translate(dx, dy, dz)
        self._min_p = None
        self._max_p = None

    def scale(self, sx, sy, sz):
        self._vb.scale(sx, sy, sz)
        self._min_p = None
        self._max_p = None

    def ntriangles(self):
        return self._tb.size()

    def bbox_triangle(self, idx):
        v = self._tb.get(idx)
        if v:
            return self._vb.bbox_triangle(v[0], v[1], v[2])
        raise ValueError("Mesh Index Erorr %i" % idx)

    @property
    def vbuffer(self):
        return self._vb.addr()

    @property
    def tbuffer(self):
        return self._tb.addr()

    def get_points(self, idx):
        v0, v1, v2 =  self._tb.get(idx)
        p0 = self._vb.get(v0)
        p1 = self._vb.get(v1)
        p2 = self._vb.get(v2)
        return p0, p1, p2

    @classmethod
    def isect_triangles_shader(cls):
        label = 'ray_triangle_isect_%s' % id(cls)
        tri_isect = ray_triangle_isect_shader(label, isect_bool=False)

        code = """

addr = mesh.lin_arrays + idx_in_array
ntri = resolve(addr, int)
if ntri == 0:
    return 0
isect_ocur = 0
idx = 0
addr = addr + 4
vbuffer = mesh.vbuffer
tbuffer = mesh.tbuffer
tb_item_size = 12
vb_item_size = 16
while idx < ntri:
    idx_triangle = resolve(addr, int)
    offset = idx_triangle * tb_item_size
    ind_addr = tbuffer + offset
    p0_idx = resolve(ind_addr, int)
    ind_addr = ind_addr + 4
    p1_idx = resolve(ind_addr, int)
    ind_addr = ind_addr + 4
    p2_idx = resolve(ind_addr, int)

    offset = p0_idx * vb_item_size
    paddr = vbuffer + offset
    p0 = resolve(paddr, vec3)
    offset = p1_idx * vb_item_size
    paddr = vbuffer + offset
    p1 = resolve(paddr, vec3)
    offset = p2_idx * vb_item_size
    paddr = vbuffer + offset
    p2 = resolve(paddr, vec3)

    ret = %s(ray, p0, p1, p2, min_dist, hitpoint)
    if ret:
        isect_ocur = 1
        min_dist = hitpoint.t
        # we save points for calculation of normal
        saved_p0 = p0
        saved_p1 = p1
        saved_p2 = p2

    idx = idx + 1
    addr = addr + 4

if isect_ocur:
    p10 = saved_p1 - saved_p0
    p20 = saved_p2 - saved_p0
    normal = cross(p10, p20)
    hitpoint.normal = normalize(normal)
    hitpoint.u = 0.0
    hitpoint.v = 0.0

return isect_ocur

        """ % label

        args = []
        mesh = FlatMesh(VertexBuffer(), TriangleBuffer(), mat_idx=0)

        func_args = [StructArgPtr('ray', Ray.factory()),
                     StructArgPtr('mesh', mesh),
                     IntArg('idx_in_array', 0),
                     FloatArg('min_dist', 0.0),
                     StructArgPtr('hitpoint', HitPoint.factory())]

        shader_name = 'isect_flat_triangles_%s' % id(cls)
        shader = Shader(code=code, args=args, name=shader_name,
                        func_args=func_args, is_func=True)

        isect_shader = DependencyShader(shader, [tri_isect])
        return isect_shader

    @classmethod
    def isect_triangles_b_shader(cls):
        label = 'ray_triangle_isect_b_%s' % id(cls)
        tri_isect = ray_triangle_isect_shader(label, isect_bool=True)

        code = """

addr = mesh.lin_arrays + idx_in_array
ntri = resolve(addr, int)
if ntri == 0:
    return 0
idx = 0
addr = addr + 4
vbuffer = mesh.vbuffer
tbuffer = mesh.tbuffer
tb_item_size = 12
vb_item_size = 16
while idx < ntri:
    idx_triangle = resolve(addr, int)
    offset = idx_triangle * tb_item_size
    ind_addr = tbuffer + offset
    p0_idx = resolve(ind_addr, int)
    ind_addr = ind_addr + 4
    p1_idx = resolve(ind_addr, int)
    ind_addr = ind_addr + 4
    p2_idx = resolve(ind_addr, int)

    offset = p0_idx * vb_item_size
    paddr = vbuffer + offset
    p0 = resolve(paddr, vec3)
    offset = p1_idx * vb_item_size
    paddr = vbuffer + offset
    p1 = resolve(paddr, vec3)
    offset = p2_idx * vb_item_size
    paddr = vbuffer + offset
    p2 = resolve(paddr, vec3)

    ret = %s(ray, p0, p1, p2, min_dist)
    if ret:
        return 1

    idx = idx + 1
    addr = addr + 4

return 0

        """ % label

        args = []
        mesh = FlatMesh(VertexBuffer(), TriangleBuffer(), mat_idx=0)

        func_args = [StructArgPtr('ray', Ray.factory()),
                     StructArgPtr('mesh', mesh),
                     IntArg('idx_in_array', 0),
                     FloatArg('min_dist', 0.0)]

        shader_name = 'isect_flat_triangles_b_%s' % id(cls)
        shader = Shader(code=code, args=args, name=shader_name,
                        func_args=func_args, is_func=True)

        isect_shader = DependencyShader(shader, [tri_isect])
        return isect_shader


    def ray_triangle(self, ray, idx, min_dist = 999999.0):
        v0, v1, v2 =  self._tb.get(idx)
        p0 = self._vb.get(v0)
        p1 = self._vb.get(v1)
        p2 = self._vb.get(v2)

        a = p0[0] - p1[0]
        b = p0[0] - p2[0] 
        c = ray.direction.x
        d = p0[0] - ray.origin.x
        e = p0[1] - p1[1]
        f = p0[1] - p2[1]
        g = ray.direction.y
        h = p0[1] - ray.origin.y
        i = p0[2] - p1[2] 
        j = p0[2] - p2[2]
        k = ray.direction.z
        l = p0[2] - ray.origin.z

        m = f * k - g * j
        n = h * k - g * l
        p = f * l - h * j
        q = g * i - e * k
        s = e * j - f * i

        temp3 =  (a * m + b * q + c * s)
        if temp3 == 0.0: return False
        inv_denom = 1.0 / temp3

        e1 = d * m - b * n - c * p
        beta = e1 * inv_denom

        if beta < 0.0: return False

        r = e * l - h * i
        e2 = a * n + d * q + c * r
        gamma = e2 * inv_denom

        if gamma < 0.0: return False

        if beta + gamma > 1.0: return False

        e3 = a * p - b * r + d * s
        t = e3 * inv_denom

        if t < 0.0001: return False # self-intersection

        hit_point = ray.origin + ray.direction * t

        normal0 = Vector3(p0[0], p0[1], p0[2])
        normal1 = Vector3(p1[0], p1[1], p1[2])
        normal2 = Vector3(p2[0], p2[1], p2[2])
        normal = (normal1 - normal0).cross(normal2 - normal0)
        normal.normalize()
        u = v = 0.0

        return HitPoint(t, hit_point, normal, self.mat_idx, u, v)

    def triangle_box_overlap(self, box_center, half_size, idx_triangle):
        v0, v1, v2 =  self._tb.get(idx_triangle)
        p0 = self._vb.get(v0)
        p1 = self._vb.get(v1)
        p2 = self._vb.get(v2)
        ret = tri_box_overlap(box_center, half_size, (p0, p1, p2))
        return ret

    def area(self):
        ntriangles = min(4000, self._tb.size())
        area = 0.0
        for i in range(ntriangles):
            idx = int(random() * self._tb.size())
            v0, v1, v2 =  self._tb.get(idx)
            p0 = self._vb.get(v0)
            p0 = Vector3(p0[0], p0[1], p0[2])
            p1 = self._vb.get(v1)
            p1 = Vector3(p1[0], p1[1], p1[2])
            p2 = self._vb.get(v2)
            p2 = Vector3(p2[0], p2[1], p2[2])
            area += (p1 - p0).cross(p2 - p0).length() * 0.5

        total_area = (area / ntriangles) * self._tb.size()
        return total_area

    def light_sample(self, spectrum):
        inv_area = 1.0 / self.area()

        code = """
tmp = random() * ntriangles
tmp = int(tmp)
if tmp < 0:
    tmp = 0
if tmp >= ntriangles:
    tmp = ntriangles - 1
idx_triangle = tmp

tb_item_size = 12
vb_item_size = 16
vbuffer = mesh.vbuffer
tbuffer = mesh.tbuffer

offset = idx_triangle * tb_item_size
ind_addr = tbuffer + offset
p0_idx = resolve(ind_addr, int)
ind_addr = ind_addr + 4
p1_idx = resolve(ind_addr, int)
ind_addr = ind_addr + 4
p2_idx = resolve(ind_addr, int)

offset = p0_idx * vb_item_size
paddr = vbuffer + offset
p0 = resolve(paddr, vec3)
offset = p1_idx * vb_item_size
paddr = vbuffer + offset
p1 = resolve(paddr, vec3)
offset = p2_idx * vb_item_size
paddr = vbuffer + offset
p2 = resolve(paddr, vec3)

r1 = random()
tmp = 1.0 - r1
tmp = sqrt(tmp)
beta = 1.0 - tmp
gamma = tmp * random()
shadepoint.light_position = (1.0 - beta - gamma) * p0 + beta * p1 + gamma * p2
shadepoint.light_pdf = inv_area

p10 = p1 - p0
p20 = p2 - p0
normal = cross(p10, p20)
shadepoint.light_normal = normalize(normal)
        """
        inv_area = FloatArg('inv_area', inv_area)
        ntriangles = IntArg('ntriangles', self._tb.size())
        mesh = StructArg('mesh', self)
        args = [inv_area, ntriangles, mesh]

        func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                     StructArgPtr('shadepoint', ShadePoint.factory(spectrum))]

        name = 'flatmesh_sample_%i' % id(self)
        return Shader(code=code, args=args, name=name,
                      func_args=func_args, is_func=True)

    def light_pdf(self, spectrum):
        inv_area = 1.0 / self.area()

        code = """
shadepoint.light_pdf = inv_area
        """
        inv_area = FloatArg('inv_area', inv_area)
        args = [inv_area]
        func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                     StructArgPtr('shadepoint', ShadePoint.factory(spectrum))]

        name = 'flatmesh_light_pdf_%i' % id(self)
        return Shader(code=code, args=args, name=name,
                      func_args=func_args, is_func=True)

    def output(self, directory, relative_name):
        full_path = os.path.join(directory, relative_name) 
        if not os.path.isfile(full_path):
            save_mesh_data(full_path, vb=self._vb, tb=self._tb, grid=self._grid)

        typ = 'type = Mesh\n'
        fname = 'fname = %s\n' % relative_name
        return typ + fname


register_struct(FlatMesh, 'FlatMesh', fields=[('vbuffer', PointerArg),
                ('tbuffer', PointerArg), ('mat_idx', IntArg),
                ('bbox_min', Vec3Arg), ('bbox_max', Vec3Arg),
                ('nx', IntArg), ('ny', IntArg), ('nz', IntArg),
                ('cells', PointerArg), ('lin_arrays', PointerArg),
                ('light_id', IntArg)],
                factory=lambda: FlatMesh(VertexBuffer(), TriangleBuffer(), 0))


class FlatUVMesh(BaseMesh):
    def __init__(self, vb, tb, mat_idx=0, light_id=-1):
        super(FlatUVMesh, self).__init__()

        if not isinstance(vb, VertexUVBuffer):
            raise ValueError("Wrong vertex buffer", vb)
        if not isinstance(tb, TriangleBuffer):
            raise ValueError("Wrong triangle buffer", tb)

        self._vb = vb
        self._tb = tb
        self.mat_idx = mat_idx
        self.light_id = light_id

        self._min_p = None
        self._max_p = None

    @classmethod
    def empty_mesh(cls):
        return FlatUVMesh(VertexUVBuffer(), TriangleBuffer(), mat_idx=0)

    def bbox(self):
        if self._min_p is None or self._max_p is None:
            min_p, max_p = self._vb.bbox()
            self._min_p = min_p
            self._max_p = max_p

        min_p = self._min_p
        max_p = self._max_p
        p0 = Vector3(min_p[0], min_p[1], min_p[2])
        p1 = Vector3(max_p[0], max_p[1], max_p[2])
        return BBox(p0, p1)

    def translate(self, dx, dy, dz):
        self._vb.translate(dx, dy, dz)
        self._min_p = None
        self._max_p = None

    def scale(self, sx, sy, sz):
        self._vb.scale(sx, sy, sz)
        self._min_p = None
        self._max_p = None

    def ntriangles(self):
        return self._tb.size()

    def bbox_triangle(self, idx):
        v = self._tb.get(idx)
        if v:
            return self._vb.bbox_triangle(v[0], v[1], v[2])
        raise ValueError("Mesh Index Erorr %i" % idx)

    @property
    def vbuffer(self):
        return self._vb.addr()

    @property
    def tbuffer(self):
        return self._tb.addr()

    def get_points(self, idx):
        v0, v1, v2 =  self._tb.get(idx)
        p0, uv0 = self._vb.get(v0)
        p1, uv1 = self._vb.get(v1)
        p2, uv2 = self._vb.get(v2)
        return p0, p1, p2

    @classmethod
    def isect_triangles_shader(cls):
        label = 'ray_triangle_isect_%s' % id(cls)
        tri_isect = ray_triangle_isect_shader(label, isect_bool=False)

        code = """

addr = mesh.lin_arrays + idx_in_array
ntri = resolve(addr, int)
if ntri == 0:
    return 0
isect_ocur = 0
idx = 0
addr = addr + 4
vbuffer = mesh.vbuffer
tbuffer = mesh.tbuffer
tb_item_size = 12
vb_item_size = 32
while idx < ntri:
    idx_triangle = resolve(addr, int)
    offset = idx_triangle * tb_item_size
    ind_addr = tbuffer + offset
    p0_idx = resolve(ind_addr, int)
    ind_addr = ind_addr + 4
    p1_idx = resolve(ind_addr, int)
    ind_addr = ind_addr + 4
    p2_idx = resolve(ind_addr, int)

    offset = p0_idx * vb_item_size
    paddr = vbuffer + offset
    p0 = resolve(paddr, vec3)
    offset = p1_idx * vb_item_size
    paddr = vbuffer + offset
    p1 = resolve(paddr, vec3)
    offset = p2_idx * vb_item_size
    paddr = vbuffer + offset
    p2 = resolve(paddr, vec3)

    ret = %s(ray, p0, p1, p2, min_dist, hitpoint)
    if ret:
        isect_ocur = 1
        min_dist = hitpoint.t
        beta = hitpoint.u
        gamma = hitpoint.v
        # we save points for calculation of normal
        saved_idx = idx
        saved_p0 = p0
        saved_p1 = p1
        saved_p2 = p2
        sp0_idx = p0_idx
        sp1_idx = p1_idx
        sp2_idx = p2_idx

    idx = idx + 1
    addr = addr + 4

if isect_ocur:
    p10 = saved_p1 - saved_p0
    p20 = saved_p2 - saved_p0
    normal = cross(p10, p20)
    hitpoint.normal = normalize(normal)

    offset = sp0_idx * vb_item_size + 16
    paddr = vbuffer + offset
    uv0 = resolve(paddr, vec2)
    offset = sp1_idx * vb_item_size + 16
    paddr = vbuffer + offset
    uv1 = resolve(paddr, vec2)
    offset = sp2_idx * vb_item_size + 16
    paddr = vbuffer + offset
    uv2 = resolve(paddr, vec2)

    hitpoint.u = uv0[0] * (1.0 - beta - gamma) + beta * uv1[0] + gamma * uv2[0]
    hitpoint.v = uv0[1] * (1.0 - beta - gamma) + beta * uv1[1] + gamma * uv2[1]

return isect_ocur

        """ % label

        args = []
        mesh = FlatUVMesh(VertexUVBuffer(), TriangleBuffer(), mat_idx=0)

        func_args = [StructArgPtr('ray', Ray.factory()),
                     StructArgPtr('mesh', mesh),
                     IntArg('idx_in_array', 0),
                     FloatArg('min_dist', 0.0),
                     StructArgPtr('hitpoint', HitPoint.factory())]

        shader_name = 'isect_flat_triangles_%s' % id(cls)
        shader = Shader(code=code, args=args, name=shader_name,
                        func_args=func_args, is_func=True)

        isect_shader = DependencyShader(shader, [tri_isect])
        return isect_shader

    @classmethod
    def isect_triangles_b_shader(cls):
        label = 'ray_triangle_isect_b_%s' % id(cls)
        tri_isect = ray_triangle_isect_shader(label, isect_bool=True)

        code = """

addr = mesh.lin_arrays + idx_in_array
ntri = resolve(addr, int)
if ntri == 0:
    return 0
idx = 0
addr = addr + 4
vbuffer = mesh.vbuffer
tbuffer = mesh.tbuffer
tb_item_size = 12
vb_item_size = 32
while idx < ntri:
    idx_triangle = resolve(addr, int)
    offset = idx_triangle * tb_item_size
    ind_addr = tbuffer + offset
    p0_idx = resolve(ind_addr, int)
    ind_addr = ind_addr + 4
    p1_idx = resolve(ind_addr, int)
    ind_addr = ind_addr + 4
    p2_idx = resolve(ind_addr, int)

    offset = p0_idx * vb_item_size
    paddr = vbuffer + offset
    p0 = resolve(paddr, vec3)
    offset = p1_idx * vb_item_size
    paddr = vbuffer + offset
    p1 = resolve(paddr, vec3)
    offset = p2_idx * vb_item_size
    paddr = vbuffer + offset
    p2 = resolve(paddr, vec3)

    ret = %s(ray, p0, p1, p2, min_dist)
    if ret:
        return 1

    idx = idx + 1
    addr = addr + 4

return 0

        """ % label

        args = []
        mesh = FlatUVMesh(VertexUVBuffer(), TriangleBuffer(), mat_idx=0)

        func_args = [StructArgPtr('ray', Ray.factory()),
                     StructArgPtr('mesh', mesh),
                     IntArg('idx_in_array', 0),
                     FloatArg('min_dist', 0.0)]

        shader_name = 'isect_flat_triangles_b_%s' % id(cls)
        shader = Shader(code=code, args=args, name=shader_name,
                        func_args=func_args, is_func=True)

        isect_shader = DependencyShader(shader, [tri_isect])
        return isect_shader

    def ray_triangle(self, ray, idx, min_dist = 999999.0):
        v0, v1, v2 =  self._tb.get(idx)
        p0, uv0 = self._vb.get(v0)
        p1, uv1 = self._vb.get(v1)
        p2, uv2 = self._vb.get(v2)

        a = p0[0] - p1[0]
        b = p0[0] - p2[0] 
        c = ray.direction.x
        d = p0[0] - ray.origin.x
        e = p0[1] - p1[1]
        f = p0[1] - p2[1]
        g = ray.direction.y
        h = p0[1] - ray.origin.y
        i = p0[2] - p1[2] 
        j = p0[2] - p2[2]
        k = ray.direction.z
        l = p0[2] - ray.origin.z

        m = f * k - g * j
        n = h * k - g * l
        p = f * l - h * j
        q = g * i - e * k
        s = e * j - f * i

        temp3 =  (a * m + b * q + c * s)
        if temp3 == 0.0: return False
        inv_denom = 1.0 / temp3

        e1 = d * m - b * n - c * p
        beta = e1 * inv_denom

        if beta < 0.0: return False

        r = e * l - h * i
        e2 = a * n + d * q + c * r
        gamma = e2 * inv_denom

        if gamma < 0.0: return False

        if beta + gamma > 1.0: return False

        e3 = a * p - b * r + d * s
        t = e3 * inv_denom

        if t < 0.0001: return False # self-intersection

        hit_point = ray.origin + ray.direction * t

        normal0 = Vector3(p0[0], p0[1], p0[2])
        normal1 = Vector3(p1[0], p1[1], p1[2])
        normal2 = Vector3(p2[0], p2[1], p2[2])
        normal = (normal1 - normal0).cross(normal2 - normal0)
        normal.normalize()

        u = uv0[0] * (1.0 - beta - gamma) + beta * uv1[0] + gamma * uv2[0]
        v = uv0[1] * (1.0 - beta - gamma) + beta * uv1[1] + gamma * uv2[1]

        return HitPoint(t, hit_point, normal, self.mat_idx, u, v)

    def area(self):
        ntriangles = min(4000, self._tb.size())
        area = 0.0
        for i in range(ntriangles):
            idx = int(random() * self._tb.size())
            v0, v1, v2 =  self._tb.get(idx)
            p0, uv0 = self._vb.get(v0)
            p0 = Vector3(p0[0], p0[1], p0[2])
            p1, uv1 = self._vb.get(v1)
            p1 = Vector3(p1[0], p1[1], p1[2])
            p2, uv2 = self._vb.get(v2)
            p2 = Vector3(p2[0], p2[1], p2[2])
            area += (p1 - p0).cross(p2 - p0).length() * 0.5

        total_area = (area / ntriangles) * self._tb.size()
        return total_area

    def light_sample(self, spectrum):
        inv_area = 1.0 / self.area()

        code = """
tmp = random() * ntriangles
tmp = int(tmp)
if tmp < 0:
    tmp = 0
if tmp >= ntriangles:
    tmp = ntriangles - 1
idx_triangle = tmp

vbuffer = mesh.vbuffer
tbuffer = mesh.tbuffer
tb_item_size = 12
vb_item_size = 32
offset = idx_triangle * tb_item_size
ind_addr = tbuffer + offset
p0_idx = resolve(ind_addr, int)
ind_addr = ind_addr + 4
p1_idx = resolve(ind_addr, int)
ind_addr = ind_addr + 4
p2_idx = resolve(ind_addr, int)

offset = p0_idx * vb_item_size
paddr = vbuffer + offset
p0 = resolve(paddr, vec3)
offset = p1_idx * vb_item_size
paddr = vbuffer + offset
p1 = resolve(paddr, vec3)
offset = p2_idx * vb_item_size
paddr = vbuffer + offset
p2 = resolve(paddr, vec3)

r1 = random()
tmp = 1.0 - r1
tmp = sqrt(tmp)
beta = 1.0 - tmp
gamma = tmp * random()
shadepoint.light_position = (1.0 - beta - gamma) * p0 + beta * p1 + gamma * p2
shadepoint.light_pdf = inv_area

p10 = p1 - p0
p20 = p2 - p0
normal = cross(p10, p20)
shadepoint.light_normal = normalize(normal)
        """
        inv_area = FloatArg('inv_area', inv_area)
        ntriangles = IntArg('ntriangles', self._tb.size())
        mesh = StructArg('mesh', self)
        args = [inv_area, ntriangles, mesh]

        func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                     StructArgPtr('shadepoint', ShadePoint.factory(spectrum))]

        name = 'flatuvmesh_sample_%i' % id(self)
        return Shader(code=code, args=args, name=name,
                      func_args=func_args, is_func=True)

    def light_pdf(self, spectrum):
        inv_area = 1.0 / self.area()

        code = """
shadepoint.light_pdf = inv_area
        """
        inv_area = FloatArg('inv_area', inv_area)
        args = [inv_area]
        func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                     StructArgPtr('shadepoint', ShadePoint.factory(spectrum))]

        name = 'flatuvmesh_light_pdf_%i' % id(self)
        return Shader(code=code, args=args, name=name,
                      func_args=func_args, is_func=True)

    def triangle_box_overlap(self, box_center, half_size, idx_triangle):
        v0, v1, v2 =  self._tb.get(idx_triangle)
        p0, uv0 = self._vb.get(v0)
        p1, uv1 = self._vb.get(v1)
        p2, uv2 = self._vb.get(v2)
        ret = tri_box_overlap(box_center, half_size, (p0, p1, p2))
        return ret

    def output(self, directory, relative_name):
        full_path = os.path.join(directory, relative_name) 
        if not os.path.isfile(full_path):
            save_mesh_data(full_path, vb=self._vb, tb=self._tb, grid=self._grid)

        typ = 'type = Mesh\n'
        fname = 'fname = %s\n' % relative_name
        return typ + fname

register_struct(FlatUVMesh, 'FlatUVMesh', fields=[('vbuffer', PointerArg),
                ('tbuffer', PointerArg), ('mat_idx', IntArg),
                ('bbox_min', Vec3Arg), ('bbox_max', Vec3Arg),
                ('nx', IntArg), ('ny', IntArg), ('nz', IntArg),
                ('cells', PointerArg), ('lin_arrays', PointerArg),
                ('light_id', IntArg)],
                factory=lambda: FlatUVMesh(VertexUVBuffer(), TriangleBuffer(), 0))


class SmoothUVMesh(BaseMesh):
    def __init__(self, vb, tb, mat_idx=0, light_id=-1):
        super(SmoothUVMesh, self).__init__()

        if not isinstance(vb, VertexNUVBuffer):
            raise ValueError("Wrong vertex buffer", vb)
        if not isinstance(tb, TriangleBuffer):
            raise ValueError("Wrong triangle buffer", tb)

        self._vb = vb
        self._tb = tb
        self.mat_idx = mat_idx
        self.light_id = light_id

        self._min_p = None
        self._max_p = None

    @classmethod
    def empty_mesh(cls):
        return SmoothUVMesh(VertexNUVBuffer(), TriangleBuffer(), mat_idx=0)

    def bbox(self):
        if self._min_p is None or self._max_p is None:
            min_p, max_p = self._vb.bbox()
            self._min_p = min_p
            self._max_p = max_p

        min_p = self._min_p
        max_p = self._max_p
        p0 = Vector3(min_p[0], min_p[1], min_p[2])
        p1 = Vector3(max_p[0], max_p[1], max_p[2])
        return BBox(p0, p1)

    def translate(self, dx, dy, dz):
        self._vb.translate(dx, dy, dz)
        self._min_p = None
        self._max_p = None

    def scale(self, sx, sy, sz):
        self._vb.scale(sx, sy, sz)
        self._min_p = None
        self._max_p = None

    def ntriangles(self):
        return self._tb.size()

    def bbox_triangle(self, idx):
        v = self._tb.get(idx)
        if v:
            return self._vb.bbox_triangle(v[0], v[1], v[2])
        raise ValueError("Mesh Index Erorr %i" % idx)

    @property
    def vbuffer(self):
        return self._vb.addr()

    @property
    def tbuffer(self):
        return self._tb.addr()

    def get_points(self, idx):
        v0, v1, v2 =  self._tb.get(idx)
        p0, n0, uv0 = self._vb.get(v0)
        p1, n1, uv1 = self._vb.get(v1)
        p2, n2, uv2 = self._vb.get(v2)
        return p0, p1, p2

    @classmethod
    def isect_triangles_shader(cls):
        label = 'ray_triangle_isect_%s' % id(cls)
        tri_isect = ray_triangle_isect_shader(label, isect_bool=False)

        code = """

addr = mesh.lin_arrays + idx_in_array
ntri = resolve(addr, int)
if ntri == 0:
    return 0
isect_ocur = 0
idx = 0
addr = addr + 4
vbuffer = mesh.vbuffer
tbuffer = mesh.tbuffer
tb_item_size = 12
vb_item_size = 48
while idx < ntri:
    idx_triangle = resolve(addr, int)
    offset = idx_triangle * tb_item_size
    ind_addr = tbuffer + offset
    p0_idx = resolve(ind_addr, int)
    ind_addr = ind_addr + 4
    p1_idx = resolve(ind_addr, int)
    ind_addr = ind_addr + 4
    p2_idx = resolve(ind_addr, int)

    offset = p0_idx * vb_item_size
    paddr = vbuffer + offset
    p0 = resolve(paddr, vec3)
    offset = p1_idx * vb_item_size
    paddr = vbuffer + offset
    p1 = resolve(paddr, vec3)
    offset = p2_idx * vb_item_size
    paddr = vbuffer + offset
    p2 = resolve(paddr, vec3)

    ret = %s(ray, p0, p1, p2, min_dist, hitpoint)
    if ret:
        isect_ocur = 1
        min_dist = hitpoint.t
        beta = hitpoint.u
        gamma = hitpoint.v
        # we save points for calculation of normal
        saved_idx = idx
        sp0_idx = p0_idx
        sp1_idx = p1_idx
        sp2_idx = p2_idx

    idx = idx + 1
    addr = addr + 4

if isect_ocur:
    offset = sp0_idx * vb_item_size + 16
    paddr = vbuffer + offset
    n0 = resolve(paddr, vec3)
    paddr = paddr + 16
    uv0 = resolve(paddr, vec2)

    offset = sp1_idx * vb_item_size + 16
    paddr = vbuffer + offset
    n1 = resolve(paddr, vec3)
    paddr = paddr + 16
    uv1 = resolve(paddr, vec2)

    offset = sp2_idx * vb_item_size + 16
    paddr = vbuffer + offset
    n2 = resolve(paddr, vec3)
    paddr = paddr + 16
    uv2 = resolve(paddr, vec2)

    normal = n0 * (1.0 - beta - gamma) + beta * n1 + gamma * n2  
    hitpoint.normal = normalize(normal)

    hitpoint.u = uv0[0] * (1.0 - beta - gamma) + beta * uv1[0] + gamma * uv2[0]
    hitpoint.v = uv0[1] * (1.0 - beta - gamma) + beta * uv1[1] + gamma * uv2[1]

return isect_ocur

        """ % label

        args = []
        mesh = SmoothUVMesh(VertexNUVBuffer(), TriangleBuffer(), mat_idx=0)

        func_args = [StructArgPtr('ray', Ray.factory()),
                     StructArgPtr('mesh', mesh),
                     IntArg('idx_in_array', 0),
                     FloatArg('min_dist', 0.0),
                     StructArgPtr('hitpoint', HitPoint.factory())]

        shader_name = 'isect_flat_triangles_%s' % id(cls)
        shader = Shader(code=code, args=args, name=shader_name,
                        func_args=func_args, is_func=True)

        isect_shader = DependencyShader(shader, [tri_isect])
        return isect_shader

    @classmethod
    def isect_triangles_b_shader(cls):
        label = 'ray_triangle_isect_b_%s' % id(cls)
        tri_isect = ray_triangle_isect_shader(label, isect_bool=True)

        code = """

addr = mesh.lin_arrays + idx_in_array
ntri = resolve(addr, int)
if ntri == 0:
    return 0
idx = 0
addr = addr + 4
vbuffer = mesh.vbuffer
tbuffer = mesh.tbuffer
tb_item_size = 12
vb_item_size = 48
while idx < ntri:
    idx_triangle = resolve(addr, int)
    offset = idx_triangle * tb_item_size
    ind_addr = tbuffer + offset
    p0_idx = resolve(ind_addr, int)
    ind_addr = ind_addr + 4
    p1_idx = resolve(ind_addr, int)
    ind_addr = ind_addr + 4
    p2_idx = resolve(ind_addr, int)

    offset = p0_idx * vb_item_size
    paddr = vbuffer + offset
    p0 = resolve(paddr, vec3)
    offset = p1_idx * vb_item_size
    paddr = vbuffer + offset
    p1 = resolve(paddr, vec3)
    offset = p2_idx * vb_item_size
    paddr = vbuffer + offset
    p2 = resolve(paddr, vec3)

    ret = %s(ray, p0, p1, p2, min_dist)
    if ret:
        return 1

    idx = idx + 1
    addr = addr + 4

return 0

        """ % label

        args = []
        mesh = SmoothUVMesh(VertexNUVBuffer(), TriangleBuffer(), mat_idx=0)

        func_args = [StructArgPtr('ray', Ray.factory()),
                     StructArgPtr('mesh', mesh),
                     IntArg('idx_in_array', 0),
                     FloatArg('min_dist', 0.0)]

        shader_name = 'isect_flat_triangles_b_%s' % id(cls)
        shader = Shader(code=code, args=args, name=shader_name,
                        func_args=func_args, is_func=True)

        isect_shader = DependencyShader(shader, [tri_isect])
        return isect_shader

    def ray_triangle(self, ray, idx, min_dist = 999999.0):
        v0, v1, v2 =  self._tb.get(idx)
        p0, n0, uv0 = self._vb.get(v0)
        p1, n1, uv1 = self._vb.get(v1)
        p2, n2, uv2 = self._vb.get(v2)

        a = p0[0] - p1[0]
        b = p0[0] - p2[0] 
        c = ray.direction.x
        d = p0[0] - ray.origin.x
        e = p0[1] - p1[1]
        f = p0[1] - p2[1]
        g = ray.direction.y
        h = p0[1] - ray.origin.y
        i = p0[2] - p1[2] 
        j = p0[2] - p2[2]
        k = ray.direction.z
        l = p0[2] - ray.origin.z

        m = f * k - g * j
        n = h * k - g * l
        p = f * l - h * j
        q = g * i - e * k
        s = e * j - f * i

        temp3 =  (a * m + b * q + c * s)
        if temp3 == 0.0: return False
        inv_denom = 1.0 / temp3

        e1 = d * m - b * n - c * p
        beta = e1 * inv_denom

        if beta < 0.0: return False

        r = e * l - h * i
        e2 = a * n + d * q + c * r
        gamma = e2 * inv_denom

        if gamma < 0.0: return False

        if beta + gamma > 1.0: return False

        e3 = a * p - b * r + d * s
        t = e3 * inv_denom

        if t < 0.0001: return False # self-intersection

        hit_point = ray.origin + ray.direction * t

        normal0 = Vector3(n0[0], n0[1], n0[2])
        normal1 = Vector3(n1[0], n1[1], n1[2])
        normal2 = Vector3(n2[0], n2[1], n2[2])

        normal = normal0 * (1.0 - beta - gamma) + beta * normal1 + gamma * normal2  
        normal.normalize()

        u = uv0[0] * (1.0 - beta - gamma) + beta * uv1[0] + gamma * uv2[0]
        v = uv0[1] * (1.0 - beta - gamma) + beta * uv1[1] + gamma * uv2[1]

        return HitPoint(t, hit_point, normal, self.mat_idx, u, v)

    def area(self):
        ntriangles = min(4000, self._tb.size())
        area = 0.0
        for i in range(ntriangles):
            idx = int(random() * self._tb.size())
            v0, v1, v2 =  self._tb.get(idx)
            p0, n0, uv0 = self._vb.get(v0)
            p0 = Vector3(p0[0], p0[1], p0[2])
            p1, n1, uv1 = self._vb.get(v1)
            p1 = Vector3(p1[0], p1[1], p1[2])
            p2, n2, uv2 = self._vb.get(v2)
            p2 = Vector3(p2[0], p2[1], p2[2])
            area += (p1 - p0).cross(p2 - p0).length() * 0.5

        total_area = (area / ntriangles) * self._tb.size()
        return total_area

    def light_sample(self, spectrum):
        inv_area = 1.0 / self.area()

        code = """
tmp = random() * ntriangles
tmp = int(tmp)
if tmp < 0:
    tmp = 0
if tmp >= ntriangles:
    tmp = ntriangles - 1
idx_triangle = tmp

vbuffer = mesh.vbuffer
tbuffer = mesh.tbuffer
tb_item_size = 12
vb_item_size = 48
offset = idx_triangle * tb_item_size
ind_addr = tbuffer + offset
p0_idx = resolve(ind_addr, int)
ind_addr = ind_addr + 4
p1_idx = resolve(ind_addr, int)
ind_addr = ind_addr + 4
p2_idx = resolve(ind_addr, int)

offset = p0_idx * vb_item_size
paddr = vbuffer + offset
p0 = resolve(paddr, vec3)
offset = p1_idx * vb_item_size
paddr = vbuffer + offset
p1 = resolve(paddr, vec3)
offset = p2_idx * vb_item_size
paddr = vbuffer + offset
p2 = resolve(paddr, vec3)

r1 = random()
tmp = 1.0 - r1
tmp = sqrt(tmp)
beta = 1.0 - tmp
gamma = tmp * random()
shadepoint.light_position = (1.0 - beta - gamma) * p0 + beta * p1 + gamma * p2
shadepoint.light_pdf = inv_area

offset = p0_idx * vb_item_size + 16
paddr = vbuffer + offset
n0 = resolve(paddr, vec3)

offset = p1_idx * vb_item_size + 16
paddr = vbuffer + offset
n1 = resolve(paddr, vec3)

offset = p2_idx * vb_item_size + 16
paddr = vbuffer + offset
n2 = resolve(paddr, vec3)

normal = n0 * (1.0 - beta - gamma) + beta * n1 + gamma * n2  
shadepoint.light_normal = normalize(normal)
        """
        inv_area = FloatArg('inv_area', inv_area)
        ntriangles = IntArg('ntriangles', self._tb.size())
        mesh = StructArg('mesh', self)
        args = [inv_area, ntriangles, mesh]

        func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                     StructArgPtr('shadepoint', ShadePoint.factory(spectrum))]

        name = 'smoothuvmesh_sample_%i' % id(self)
        return Shader(code=code, args=args, name=name,
                      func_args=func_args, is_func=True)

    def light_pdf(self, spectrum):
        inv_area = 1.0 / self.area()

        code = """
shadepoint.light_pdf = inv_area
        """
        inv_area = FloatArg('inv_area', inv_area)
        args = [inv_area]
        func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                     StructArgPtr('shadepoint', ShadePoint.factory(spectrum))]

        name = 'smoothuvmesh_light_pdf_%i' % id(self)
        return Shader(code=code, args=args, name=name,
                      func_args=func_args, is_func=True)

    def triangle_box_overlap(self, box_center, half_size, idx_triangle):
        v0, v1, v2 =  self._tb.get(idx_triangle)
        p0, n0, uv0 = self._vb.get(v0)
        p1, n1, uv1 = self._vb.get(v1)
        p2, n2, uv2 = self._vb.get(v2)
        ret = tri_box_overlap(box_center, half_size, (p0, p1, p2))
        return ret

    def output(self, directory, relative_name):
        full_path = os.path.join(directory, relative_name) 
        if not os.path.isfile(full_path):
            save_mesh_data(full_path, vb=self._vb, tb=self._tb, grid=self._grid)

        typ = 'type = Mesh\n'
        fname = 'fname = %s\n' % relative_name
        return typ + fname

register_struct(SmoothUVMesh, 'SmoothUVMesh', fields=[('vbuffer', PointerArg),
                ('tbuffer', PointerArg), ('mat_idx', IntArg),
                ('bbox_min', Vec3Arg), ('bbox_max', Vec3Arg),
                ('nx', IntArg), ('ny', IntArg), ('nz', IntArg),
                ('cells', PointerArg), ('lin_arrays', PointerArg),
                ('light_id', IntArg)],
                factory=lambda: SmoothUVMesh(VertexNUVBuffer(), TriangleBuffer(), 0))


class SmoothMesh(BaseMesh):
    def __init__(self, vb, tb, mat_idx=0, light_id=-1):
        super(SmoothMesh, self).__init__()

        if not isinstance(vb, VertexNBuffer):
            raise ValueError("Wrong vertex buffer", vb)
        if not isinstance(tb, TriangleBuffer):
            raise ValueError("Wrong triangle buffer", tb)

        self._vb = vb
        self._tb = tb
        self.mat_idx = mat_idx
        self.light_id = light_id

        self._min_p = None
        self._max_p = None

    @classmethod
    def empty_mesh(cls):
        return SmoothMesh(VertexNBuffer(), TriangleBuffer(), mat_idx=0)

    def bbox(self):
        if self._min_p is None or self._max_p is None:
            min_p, max_p = self._vb.bbox()
            self._min_p = min_p
            self._max_p = max_p

        min_p = self._min_p
        max_p = self._max_p
        p0 = Vector3(min_p[0], min_p[1], min_p[2])
        p1 = Vector3(max_p[0], max_p[1], max_p[2])
        return BBox(p0, p1)

    def translate(self, dx, dy, dz):
        self._vb.translate(dx, dy, dz)
        self._min_p = None
        self._max_p = None

    def scale(self, sx, sy, sz):
        self._vb.scale(sx, sy, sz)
        self._min_p = None
        self._max_p = None

    def ntriangles(self):
        return self._tb.size()

    def bbox_triangle(self, idx):
        v = self._tb.get(idx)
        if v:
            return self._vb.bbox_triangle(v[0], v[1], v[2])
        raise ValueError("Mesh Index Erorr %i" % idx)

    @property
    def vbuffer(self):
        return self._vb.addr()

    @property
    def tbuffer(self):
        return self._tb.addr()

    def get_points(self, idx):
        v0, v1, v2 =  self._tb.get(idx)
        p0, n0 = self._vb.get(v0)
        p1, n1 = self._vb.get(v1)
        p2, n2 = self._vb.get(v2)
        return p0, p1, p2

    @classmethod
    def isect_triangles_shader(cls):
        label = 'ray_triangle_isect_%s' % id(cls)
        tri_isect = ray_triangle_isect_shader(label, isect_bool=False)

        code = """

addr = mesh.lin_arrays + idx_in_array
ntri = resolve(addr, int)
if ntri == 0:
    return 0
isect_ocur = 0
idx = 0
addr = addr + 4
vbuffer = mesh.vbuffer
tbuffer = mesh.tbuffer
tb_item_size = 12
vb_item_size = 32
while idx < ntri:
    idx_triangle = resolve(addr, int)
    offset = idx_triangle * tb_item_size
    ind_addr = tbuffer + offset
    p0_idx = resolve(ind_addr, int)
    ind_addr = ind_addr + 4
    p1_idx = resolve(ind_addr, int)
    ind_addr = ind_addr + 4
    p2_idx = resolve(ind_addr, int)

    offset = p0_idx * vb_item_size
    paddr = vbuffer + offset
    p0 = resolve(paddr, vec3)
    offset = p1_idx * vb_item_size
    paddr = vbuffer + offset
    p1 = resolve(paddr, vec3)
    offset = p2_idx * vb_item_size
    paddr = vbuffer + offset
    p2 = resolve(paddr, vec3)

    ret = %s(ray, p0, p1, p2, min_dist, hitpoint)
    if ret:
        isect_ocur = 1
        min_dist = hitpoint.t
        beta = hitpoint.u
        gamma = hitpoint.v
        # we save points for calculation of normal
        saved_idx = idx
        sp0_idx = p0_idx
        sp1_idx = p1_idx
        sp2_idx = p2_idx

    idx = idx + 1
    addr = addr + 4

if isect_ocur:
    offset = sp0_idx * vb_item_size + 16
    paddr = vbuffer + offset
    n0 = resolve(paddr, vec3)

    offset = sp1_idx * vb_item_size + 16
    paddr = vbuffer + offset
    n1 = resolve(paddr, vec3)

    offset = sp2_idx * vb_item_size + 16
    paddr = vbuffer + offset
    n2 = resolve(paddr, vec3)

    normal = n0 * (1.0 - beta - gamma) + beta * n1 + gamma * n2  
    hitpoint.normal = normalize(normal)

    hitpoint.u = 0.0
    hitpoint.v = 0.0

return isect_ocur

        """ % label

        args = []
        mesh = SmoothMesh(VertexNBuffer(), TriangleBuffer(), mat_idx=0)

        func_args = [StructArgPtr('ray', Ray.factory()),
                     StructArgPtr('mesh', mesh),
                     IntArg('idx_in_array', 0),
                     FloatArg('min_dist', 0.0),
                     StructArgPtr('hitpoint', HitPoint.factory())]

        shader_name = 'isect_flat_triangles_%s' % id(cls)
        shader = Shader(code=code, args=args, name=shader_name,
                        func_args=func_args, is_func=True)

        isect_shader = DependencyShader(shader, [tri_isect])
        return isect_shader

    @classmethod
    def isect_triangles_b_shader(cls):
        label = 'ray_triangle_isect_b_%s' % id(cls)
        tri_isect = ray_triangle_isect_shader(label, isect_bool=True)

        code = """

addr = mesh.lin_arrays + idx_in_array
ntri = resolve(addr, int)
if ntri == 0:
    return 0
idx = 0
addr = addr + 4
vbuffer = mesh.vbuffer
tbuffer = mesh.tbuffer
tb_item_size = 12
vb_item_size = 32
while idx < ntri:
    idx_triangle = resolve(addr, int)
    offset = idx_triangle * tb_item_size
    ind_addr = tbuffer + offset
    p0_idx = resolve(ind_addr, int)
    ind_addr = ind_addr + 4
    p1_idx = resolve(ind_addr, int)
    ind_addr = ind_addr + 4
    p2_idx = resolve(ind_addr, int)

    offset = p0_idx * vb_item_size
    paddr = vbuffer + offset
    p0 = resolve(paddr, vec3)
    offset = p1_idx * vb_item_size
    paddr = vbuffer + offset
    p1 = resolve(paddr, vec3)
    offset = p2_idx * vb_item_size
    paddr = vbuffer + offset
    p2 = resolve(paddr, vec3)

    ret = %s(ray, p0, p1, p2, min_dist)
    if ret:
        return 1

    idx = idx + 1
    addr = addr + 4

return 0

        """ % label

        args = []
        mesh = SmoothMesh(VertexNBuffer(), TriangleBuffer(), mat_idx=0)

        func_args = [StructArgPtr('ray', Ray.factory()),
                     StructArgPtr('mesh', mesh),
                     IntArg('idx_in_array', 0),
                     FloatArg('min_dist', 0.0)]

        shader_name = 'isect_flat_triangles_b_%s' % id(cls)
        shader = Shader(code=code, args=args, name=shader_name,
                        func_args=func_args, is_func=True)

        isect_shader = DependencyShader(shader, [tri_isect])
        return isect_shader

    def ray_triangle(self, ray, idx, min_dist = 999999.0):
        v0, v1, v2 =  self._tb.get(idx)
        p0, n0 = self._vb.get(v0)
        p1, n1 = self._vb.get(v1)
        p2, n2 = self._vb.get(v2)

        a = p0[0] - p1[0]
        b = p0[0] - p2[0] 
        c = ray.direction.x
        d = p0[0] - ray.origin.x
        e = p0[1] - p1[1]
        f = p0[1] - p2[1]
        g = ray.direction.y
        h = p0[1] - ray.origin.y
        i = p0[2] - p1[2] 
        j = p0[2] - p2[2]
        k = ray.direction.z
        l = p0[2] - ray.origin.z

        m = f * k - g * j
        n = h * k - g * l
        p = f * l - h * j
        q = g * i - e * k
        s = e * j - f * i

        temp3 =  (a * m + b * q + c * s)
        if temp3 == 0.0: return False
        inv_denom = 1.0 / temp3

        e1 = d * m - b * n - c * p
        beta = e1 * inv_denom

        if beta < 0.0: return False

        r = e * l - h * i
        e2 = a * n + d * q + c * r
        gamma = e2 * inv_denom

        if gamma < 0.0: return False

        if beta + gamma > 1.0: return False

        e3 = a * p - b * r + d * s
        t = e3 * inv_denom

        if t < 0.0001: return False # self-intersection

        hit_point = ray.origin + ray.direction * t

        normal0 = Vector3(n0[0], n0[1], n0[2])
        normal1 = Vector3(n1[0], n1[1], n1[2])
        normal2 = Vector3(n2[0], n2[1], n2[2])

        normal = normal0 * (1.0 - beta - gamma) + beta * normal1 + gamma * normal2  
        normal.normalize()

        u = v = 0.0

        return HitPoint(t, hit_point, normal, self.mat_idx, u, v)

    def area(self):
        ntriangles = min(4000, self._tb.size())
        area = 0.0
        for i in range(ntriangles):
            idx = int(random() * self._tb.size())
            v0, v1, v2 =  self._tb.get(idx)
            p0, n0 = self._vb.get(v0)
            p0 = Vector3(p0[0], p0[1], p0[2])
            p1, n1 = self._vb.get(v1)
            p1 = Vector3(p1[0], p1[1], p1[2])
            p2, n2 = self._vb.get(v2)
            p2 = Vector3(p2[0], p2[1], p2[2])
            area += (p1 - p0).cross(p2 - p0).length() * 0.5

        total_area = (area / ntriangles) * self._tb.size()
        return total_area

    def light_sample(self, spectrum):
        inv_area = 1.0 / self.area()

        code = """
tmp = random() * ntriangles
tmp = int(tmp)
if tmp < 0:
    tmp = 0
if tmp >= ntriangles:
    tmp = ntriangles - 1
idx_triangle = tmp

vbuffer = mesh.vbuffer
tbuffer = mesh.tbuffer
tb_item_size = 12
vb_item_size = 32
offset = idx_triangle * tb_item_size
ind_addr = tbuffer + offset
p0_idx = resolve(ind_addr, int)
ind_addr = ind_addr + 4
p1_idx = resolve(ind_addr, int)
ind_addr = ind_addr + 4
p2_idx = resolve(ind_addr, int)

offset = p0_idx * vb_item_size
paddr = vbuffer + offset
p0 = resolve(paddr, vec3)
offset = p1_idx * vb_item_size
paddr = vbuffer + offset
p1 = resolve(paddr, vec3)
offset = p2_idx * vb_item_size
paddr = vbuffer + offset
p2 = resolve(paddr, vec3)

r1 = random()
tmp = 1.0 - r1
tmp = sqrt(tmp)
beta = 1.0 - tmp
gamma = tmp * random()
shadepoint.light_position = (1.0 - beta - gamma) * p0 + beta * p1 + gamma * p2
shadepoint.light_pdf = inv_area

offset = p0_idx * vb_item_size + 16
paddr = vbuffer + offset
n0 = resolve(paddr, vec3)

offset = p1_idx * vb_item_size + 16
paddr = vbuffer + offset
n1 = resolve(paddr, vec3)

offset = p2_idx * vb_item_size + 16
paddr = vbuffer + offset
n2 = resolve(paddr, vec3)

normal = n0 * (1.0 - beta - gamma) + beta * n1 + gamma * n2  
shadepoint.light_normal = normalize(normal)
        """
        inv_area = FloatArg('inv_area', inv_area)
        ntriangles = IntArg('ntriangles', self._tb.size())
        mesh = StructArg('mesh', self)
        args = [inv_area, ntriangles, mesh]

        func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                     StructArgPtr('shadepoint', ShadePoint.factory(spectrum))]

        name = 'smoothmesh_sample_%i' % id(self)
        return Shader(code=code, args=args, name=name,
                      func_args=func_args, is_func=True)

    def light_pdf(self, spectrum):
        inv_area = 1.0 / self.area()

        code = """
shadepoint.light_pdf = inv_area
        """
        inv_area = FloatArg('inv_area', inv_area)
        args = [inv_area]
        func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                     StructArgPtr('shadepoint', ShadePoint.factory(spectrum))]

        name = 'smoothmesh_light_pdf_%i' % id(self)
        return Shader(code=code, args=args, name=name,
                      func_args=func_args, is_func=True)

    def triangle_box_overlap(self, box_center, half_size, idx_triangle):
        v0, v1, v2 =  self._tb.get(idx_triangle)
        p0, n0 = self._vb.get(v0)
        p1, n1 = self._vb.get(v1)
        p2, n2 = self._vb.get(v2)
        ret = tri_box_overlap(box_center, half_size, (p0, p1, p2))
        return ret

    def output(self, directory, relative_name):
        full_path = os.path.join(directory, relative_name) 
        if not os.path.isfile(full_path):
            save_mesh_data(full_path, vb=self._vb, tb=self._tb, grid=self._grid)

        typ = 'type = Mesh\n'
        fname = 'fname = %s\n' % relative_name
        return typ + fname


register_struct(SmoothMesh, 'SmoothMesh', fields=[('vbuffer', PointerArg),
                ('tbuffer', PointerArg), ('mat_idx', IntArg),
                ('bbox_min', Vec3Arg), ('bbox_max', Vec3Arg),
                ('nx', IntArg), ('ny', IntArg), ('nz', IntArg),
                ('cells', PointerArg), ('lin_arrays', PointerArg),
                ('light_id', IntArg)],
                factory=lambda: SmoothMesh(VertexNBuffer(), TriangleBuffer(), 0))


def create_mesh(vb, tb, mat_idx=0):

    if isinstance(vb, VertexBuffer) and isinstance(tb, TriangleBuffer):
        return FlatMesh(vb, tb, mat_idx)
    elif isinstance(vb, VertexUVBuffer) and isinstance(tb, TriangleBuffer):
        return FlatUVMesh(vb, tb, mat_idx)
    elif isinstance(vb, VertexNUVBuffer) and isinstance(tb, TriangleBuffer):
        return SmoothUVMesh(vb, tb, mat_idx)
    elif isinstance(vb, VertexNBuffer) and isinstance(tb, TriangleBuffer):
        return SmoothMesh(vb, tb, mat_idx)

    raise ValueError("Not yet supported mesh type", vb, tb)


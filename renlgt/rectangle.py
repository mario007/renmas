
from sdl import Vector3, Ray, Shader, register_struct,\
    Vec3Arg, StructArgPtr, FloatArg, IntArg

from .hitpoint import HitPoint
from .shadepoint import ShadePoint
from .shape import Shape, DependencyShader
from .bbox import BBox


class Rectangle(Shape):

    __slots__ = ['point', 'edge_a', 'edge_b', 'normal', 'mat_idx',
                 'edge_a_squared', 'edge_b_squared']

    def __init__(self, point, edge_a, edge_b, normal, mat_idx=0):

        self.point = point
        self.edge_a = edge_a
        self.edge_b = edge_b
        self.mat_idx = mat_idx

        self.normal = normal.normalize()
        self.edge_a_squared = edge_a.length_squared()
        self.edge_b_squared = edge_b.length_squared()

    def isect_b(self, ray, min_dist=999999.0):  # ray dir. must be normalized

        temp1 = ray.direction.dot(self.normal)
        if temp1 == 0.0:
            return False

        t = (self.point - ray.origin).dot(self.normal) / temp1
        if t < 0.00001:
            return False
        if t > min_dist:
            return False

        p = ray.origin + ray.direction * t
        d = p - self.point
        ddota = d.dot(self.edge_a)
        if ddota < 0.0 or ddota > self.edge_a_squared:
            return False

        ddotb = d.dot(self.edge_b)
        if ddotb < 0.0 or ddotb > self.edge_b_squared:
            return False

        return True

    @classmethod
    def isect_b_shader(cls, shader_name):
        code = """
temp1 = dot(ray.direction, rectangle.normal)
if temp1 == 0.0:
    return 0

tmp = rectangle.point - ray.origin
t = dot(tmp, rectangle.normal) / temp1

if t < 0.00001:
    return 0

if t > min_dist:
    return 0

p = ray.origin + ray.direction * t
d = p - rectangle.point

ddota = dot(d, rectangle.edge_a)
if ddota < 0.0:
    return 0
if ddota > rectangle.edge_a_squared:
    return 0

ddotb = dot(d, rectangle.edge_b)
if ddotb < 0.0:
    return 0
if ddotb > rectangle.edge_b_squared:
    return 0

return 1
        """
        func_args = [StructArgPtr('ray', Ray.factory()),
                     StructArgPtr('rectangle', Rectangle.factory()),
                     FloatArg('min_dist', 0.0)]

        shader = Shader(code=code, args=[], name=shader_name,
                        func_args=func_args, is_func=True)
        return DependencyShader(shader)

    def isect(self, ray, min_dist=999999.0):

        temp1 = ray.direction.dot(self.normal)
        if temp1 == 0.0:
            return False

        t = (self.point - ray.origin).dot(self.normal) / temp1
        if t < 0.00001:
            return False
        if t > min_dist:
            return False

        p = ray.origin + ray.direction * t
        d = p - self.point
        ddota = d.dot(self.edge_a)
        if ddota < 0.0 or ddota > self.edge_a_squared:
            return False

        ddotb = d.dot(self.edge_b)
        if ddotb < 0.0 or ddotb > self.edge_b_squared:
            return False

        return HitPoint(t, p, self.normal, self.mat_idx, 0.0, 0.0)

    @classmethod
    def isect_shader(cls, shader_name):
        code = """
temp1 = dot(ray.direction, rectangle.normal)
if temp1 == 0.0:
    return 0

tmp = rectangle.point - ray.origin
t = dot(tmp, rectangle.normal) / temp1

if t < 0.00001:
    return 0

if t > min_dist:
    return 0

p = ray.origin + ray.direction * t
d = p - rectangle.point

ddota = dot(d, rectangle.edge_a)
if ddota < 0.0:
    return 0
if ddota > rectangle.edge_a_squared:
    return 0

ddotb = dot(d, rectangle.edge_b)
if ddotb < 0.0:
    return 0
if ddotb > rectangle.edge_b_squared:
    return 0

hitpoint.t = t
hitpoint.normal = rectangle.normal
hitpoint.hit = p
hitpoint.mat_idx = rectangle.mat_idx
hitpoint.u = 0.0
hitpoint.v = 0.0
return 1

        """
        func_args = [StructArgPtr('ray', Ray.factory()),
                     StructArgPtr('rectangle', Rectangle.factory()),
                     StructArgPtr('hitpoint', HitPoint.factory()),
                     FloatArg('min_dist', 0.0)]

        shader = Shader(code=code, args=[], name=shader_name,
                        func_args=func_args, is_func=True)
        return DependencyShader(shader)

    def bbox(self):
        epsilon = 0.001

        p = self.point
        ea = self.edge_a
        eb = self.edge_b

        p0X = min(p.x, p.x + ea.x, p.x + eb.x, p.x + ea.x + eb.x) - epsilon
        p1X = max(p.x, p.x + ea.x, p.x + eb.x, p.x + ea.x + eb.x) + epsilon
        p0Y = min(p.y, p.y + ea.y, p.y + eb.y, p.y + ea.y + eb.y) - epsilon
        p1Y = max(p.y, p.y + ea.y, p.y + eb.y, p.y + ea.y + eb.y) + epsilon
        p0Z = min(p.z, p.z + ea.z, p.z + eb.z, p.z + ea.z + eb.z) - epsilon
        p1Z = max(p.z, p.z + ea.z, p.z + eb.z, p.z + ea.z + eb.z) + epsilon

        p0 = Vector3(p0X, p0Y, p0Z)
        p1 = Vector3(p1X, p1Y, p1Z)

        return BBox(p0, p1)

    def light_sample(self, spectrum):
        area = self.edge_a.length() * self.edge_b.length()
        inv_area = 1.0 / area

        code = """
rnd = random2()
shadepoint.light_pdf = inv_area
shadepoint.light_normal = normal
shadepoint.light_position = point + edge_a * rnd[0] + edge_b * rnd[1]
        """
        inv_area = FloatArg('inv_area', inv_area)
        normal = Vec3Arg('normal', self.normal)
        point = Vec3Arg('point', self.point)
        eda = Vec3Arg('edge_a', self.edge_a)
        edb = Vec3Arg('edge_b', self.edge_b)
        args = [inv_area, normal, point, eda, edb]

        func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                     StructArgPtr('shadepoint', ShadePoint.factory(spectrum))]

        name = 'rect_%i' % id(self)
        return Shader(code=code, args=args, name=name,
                      func_args=func_args, is_func=True)

    @classmethod
    def factory(cls):
        return Rectangle(Vector3(0.0, 0.0, 0.0), Vector3(1.0, 0.0, 0.0),
                         Vector3(0.0, 0.0, 1.0), Vector3(0.0, 1.0, 0.0), 0)


register_struct(Rectangle, 'Rectangle', fields=[('point', Vec3Arg),
                ('edge_a', Vec3Arg), ('edge_b', Vec3Arg),
                ('normal', Vec3Arg), ('edge_a_squared', FloatArg),
                ('edge_b_squared', FloatArg), ('mat_idx', IntArg)],
                factory=Rectangle.factory)

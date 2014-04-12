
from sdl import Vector3, Ray, Shader, register_struct,\
    Vec3Arg, StructArgPtr, FloatArg, IntArg

from .hitpoint import HitPoint
from .shape import Shape, DependencyShader
from .shader_lib import ray_triangle_isect_shader
from .bbox import BBox


class FlatTriangle(Shape):
    def __init__(self, p0, p1, p2, mat_idx=0, light_id=-1):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.mat_idx = mat_idx
        self.light_id = light_id

        self.normal = (p1 - p0).cross(p2 - p0)
        self.normal.normalize()

    def isect(self, ray, min_dist=99999.0): #ray direction must be normalized

        a = self.p0.x - self.p1.x
        b = self.p0.x - self.p2.x
        c = ray.direction.x 
        d = self.p0.x - ray.origin.x
        e = self.p0.y - self.p1.y
        f = self.p0.y - self.p2.y
        g = ray.direction.y
        h = self.p0.y - ray.origin.y
        i = self.p0.z - self.p1.z
        j = self.p0.z - self.p2.z
        k = ray.direction.z
        l = self.p0.z - ray.origin.z

        m = f * k - g * j
        n = h * k - g * l
        p = f * l - h * j
        q = g * i - e * k
        s = e * j - f * i

        temp3 =  (a * m + b * q + c * s)

        if temp3 == 0.0:
            return False
        inv_denom = 1.0 / temp3

        e1 = d * m - b * n - c * p
        beta = e1 * inv_denom

        if beta < 0.0:
            return False

        r = e * l - h * i
        e2 = a * n + d * q + c * r
        gamma = e2 * inv_denom

        if gamma < 0.0:
            return False

        if beta + gamma > 1.0:
            return False

        e3 = a * p - b * r + d * s
        t = e3 * inv_denom

        if t < 0.00001:
            return False # self-intersection

        if t > min_dist:
            return False

        hit_point = ray.origin + ray.direction * t

        return HitPoint(t, hit_point, self.normal, self.mat_idx, 0.0, 0.0)

    @classmethod
    def isect_shader(cls, shader_name):
        label = 'ray_triangle_isect_%s' % id(cls)
        tri_isect = ray_triangle_isect_shader(label, isect_bool=False)

        code = """
ret = %s(ray, triangle.p0, triangle.p1, triangle.p2, min_dist, hitpoint)
if ret:
    hitpoint.normal = triangle.normal
    hitpoint.u = 0.0
    hitpoint.v = 0.0
    hitpoint.mat_idx = triangle.mat_idx
    hitpoint.light_id = triangle.light_id
    return 1
else:
    return 0
        """ % label
        args = []
        origin = Vector3(0.0, 0.0, 0.0)
        direction = Vector3(0.0, 0.0, 0.0)
        ray = Ray(origin, direction)
        hitpoint = HitPoint(0.0, Vector3(0.0, 0.0, 0.0),
                            Vector3(0.0, 0.0, 0.0), 0, 0.0, 0.0)

        triangle = FlatTriangle(Vector3(1.0, 0.0, 0.0),
                                Vector3(0.0, 1.0, 0.0),
                                Vector3(0.0, 0.0, 1.0), 0)

        func_args = [StructArgPtr('ray', ray),
                     StructArgPtr('triangle', triangle),
                     StructArgPtr('hitpoint', hitpoint),
                     FloatArg('min_dist', 0.0)]

        shader = Shader(code=code, args=args, name=shader_name,
                        func_args=func_args, is_func=True)

        isect_shader = DependencyShader(shader, [tri_isect])
        return isect_shader


    def isect_b(self, ray, min_dist=99999.0): #ray direction must be normalized

        a = self.p0.x - self.p1.x
        b = self.p0.x - self.p2.x
        c = ray.direction.x 
        d = self.p0.x - ray.origin.x
        e = self.p0.y - self.p1.y
        f = self.p0.y - self.p2.y
        g = ray.direction.y
        h = self.p0.y - ray.origin.y
        i = self.p0.z - self.p1.z
        j = self.p0.z - self.p2.z
        k = ray.direction.z
        l = self.p0.z - ray.origin.z

        m = f * k - g * j
        n = h * k - g * l
        p = f * l - h * j
        q = g * i - e * k
        s = e * j - f * i

        temp3 =  (a * m + b * q + c * s)

        if temp3 == 0.0:
            return False
        inv_denom = 1.0 / temp3

        e1 = d * m - b * n - c * p
        beta = e1 * inv_denom

        if beta < 0.0:
            return False

        r = e * l - h * i
        e2 = a * n + d * q + c * r
        gamma = e2 * inv_denom

        if gamma < 0.0:
            return False

        if beta + gamma > 1.0:
            return False

        e3 = a * p - b * r + d * s
        t = e3 * inv_denom

        if t < 0.00001:
            return False # self-intersection

        if t > min_dist:
            return False

        return True

    def bbox(self):
        epsilon = 0.0001
        v0 = self.p0 
        v1 = self.p1
        v2 = self.p2
        minx = min(min(v0.x, v1.x), v2.x) - epsilon
        maxx = max(max(v0.x, v1.x), v2.x) + epsilon
        miny = min(min(v0.y, v1.y), v2.y) - epsilon
        maxy = max(max(v0.y, v1.y), v2.y) + epsilon
        minz = min(min(v0.z, v1.z), v2.z) - epsilon
        maxz = max(max(v0.z, v1.z), v2.z) + epsilon
        p0 = Vector3(minx, miny, minz)
        p1 = Vector3(maxx, maxy, maxz)
        return BBox(p0, p1)

    @classmethod
    def isect_b_shader(cls, shader_name):
        label = 'ray_triangle_isect_b_%s' % id(cls)
        tri_isect = ray_triangle_isect_shader(label, isect_bool=True)

        code = """
return %s(ray, triangle.p0, triangle.p1, triangle.p2, min_dist)
        """ % label
        args = []
        func_args = [StructArgPtr('ray', Ray.factory()),
                     StructArgPtr('triangle', FlatTriangle.factory()),
                     FloatArg('min_dist', 0.0)]

        shader = Shader(code=code, args=args, name=shader_name,
                        func_args=func_args, is_func=True)

        isect_shader = DependencyShader(shader, [tri_isect])
        return isect_shader

    @classmethod
    def factory(cls):
        triangle = FlatTriangle(Vector3(1.0, 0.0, 0.0),
                                Vector3(0.0, 1.0, 0.0),
                                Vector3(0.0, 0.0, 1.0), 0)
        return triangle


register_struct(FlatTriangle, 'FlatTriangle', fields=[('p0', Vec3Arg),
                ('p1', Vec3Arg), ('p2', Vec3Arg), ('normal', Vec3Arg),
                ('mat_idx', IntArg), ('light_id', IntArg)],
                factory=lambda: FlatTriangle.factory())

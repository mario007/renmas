
import math
from sdl import Vector3, Ray, Shader, register_struct,\
    Vec3Arg, StructArgPtr, FloatArg, IntArg

from .hitpoint import HitPoint
from .shape import Shape, DependencyShader


class Sphere(Shape):
    def __init__(self, origin, radius, mat_idx):
        self.origin = origin
        self.radius = radius
        self.mat_idx = mat_idx

    def isect_b(self, ray, min_dist=99999.0):  # ray dir. must be normalized
        temp = ray.origin - self.origin
        a = ray.direction.dot(ray.direction)
        b = temp.dot(ray.direction) * 2.0
        c = temp.dot(temp) - self.radius * self.radius
        disc = b * b - 4.0 * a * c

        if disc < 0.0:
            return False
        else:
            e = math.sqrt(disc)
            denom = 2.0 * a
            t = (-b - e) / denom  # smaller root
            if t > 0.0005 and t < min_dist:
                return True

            t = (-b + e) / denom  # larger root
            if t > 0.0005 and t < min_dist:
                return True
        return False

    @classmethod
    def isect_b_shader(cls, shader_name):
        code = """
temp = ray.origin - sphere.origin
r_dir = ray.direction
a = dot(r_dir, r_dir)
b = dot(temp, r_dir) * 2.0
c = dot(temp, temp) - sphere.radius * sphere.radius
disc = b * b - 4.0 * a * c

if disc < 0.0:
    return 0
e = sqrt(disc)
denom = 2.0 * a
t = (-1.0 * b - e) / denom
if t > 0.0005:
    if t < min_dist:
        return 1

t = (-1.0 * b + e) / denom
if t > 0.0005:
    if t < min_dist:
        return 1

return 0


        """
        func_args = [StructArgPtr('ray', Ray.factory()),
                     StructArgPtr('sphere', Sphere.factory()),
                     FloatArg('min_dist', 0.0)]
        shader = Shader(code=code, args=[], name=shader_name,
                        func_args=func_args, is_func=True)
        return DependencyShader(shader)

    @classmethod
    def isect_shader(cls, shader_name):
        code = """
temp = ray.origin - sphere.origin
r_dir = ray.direction
a = dot(r_dir, r_dir)
b = dot(temp, r_dir) * 2.0
c = dot(temp, temp) - sphere.radius * sphere.radius
disc = b * b - 4.0 * a * c

if disc < 0.0:
    return 0
e = sqrt(disc)
denom = 2.0 * a
t = (-1.0 * b - e) / denom
if t > 0.0005:
    if t < min_dist:
        normal = (temp + r_dir * t) * (1.0 / sphere.radius)
        hit = ray.origin + r_dir * t
        hitpoint.t = t
        hitpoint.normal = normal
        hitpoint.hit = hit
        hitpoint.mat_idx = sphere.mat_idx
        hitpoint.u = 0.0
        hitpoint.v = 0.0
        return 1

t = (-1.0 * b + e) / denom
if t > 0.0005:
    if t < min_dist:
        normal = (temp + r_dir * t) * (1.0 / sphere.radius)
        hit = ray.origin + r_dir * t
        hitpoint.t = t
        hitpoint.normal = normal
        hitpoint.hit = hit
        hitpoint.mat_idx = sphere.mat_idx
        hitpoint.u = 0.0
        hitpoint.v = 0.0
        return 1

return 0

        """
        func_args = [StructArgPtr('ray', Ray.factory()),
                     StructArgPtr('sphere', Sphere.factory()),
                     StructArgPtr('hitpoint', HitPoint.factory()),
                     FloatArg('min_dist', 0.0)]
        shader = Shader(code=code, args=[], name=shader_name,
                        func_args=func_args, is_func=True)
        return DependencyShader(shader)

    def isect(self, ray, min_dist=999999.0):  # ray dir. must be normalized
        temp = ray.origin - self.origin
        a = ray.direction.dot(ray.direction)
        b = temp.dot(ray.direction) * 2.0
        c = temp.dot(temp) - self.radius * self.radius
        disc = b * b - 4.0 * a * c

        if disc < 0.0:
            return False
        else:
            e = math.sqrt(disc)
            denom = 2.0 * a
            t = (-b - e) / denom  # smaller root
            if t > 0.0005 and t < min_dist:
                normal = (temp + ray.direction * t) * (1.0 / self.radius)
                hit_point = ray.origin + ray.direction * t
                return HitPoint(t, hit_point, normal, self.mat_idx, 0.0, 0.0)

            t = (-b + e) / denom  # larger root
            if t > 0.0005 and t < min_dist:
                normal = (temp + ray.direction * t) * (1.0 / self.radius)
                hit_point = ray.origin + ray.direction * t
                return HitPoint(t, hit_point, normal, self.mat_idx, 0.0, 0.0)
        return False

    @classmethod
    def factory(cls):
        return Sphere(Vector3(0.0, 0.0, 0.0), 0.0, 0)

register_struct(Sphere, 'Sphere', fields=[('origin', Vec3Arg),
                ('radius', FloatArg), ('mat_idx', IntArg)],
                factory=lambda: Sphere(Vector3(0.0, 0.0, 0.0), 0.0, 0))

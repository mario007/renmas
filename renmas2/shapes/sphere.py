import math
from ..core import Vector3, Shape
from .bbox import BBox
from .hitpoint import Hitpoint

class Sphere(Shape):
    def __init__(self, origin, radius, material):
        self.origin = origin
        self.radius = radius
        self.material = material

    def isect(self, ray, min_dist=999999.0): #ray direction must be normalized
        temp = ray.origin - self.origin
        a = ray.dir.dot(ray.dir)
        b = temp.dot(ray.dir) * 2.0
        c = temp.dot(temp) - self.radius * self.radius
        disc = b * b - 4.0 * a * c

        if disc < 0.0:
            return False
        else:
            e = math.sqrt(disc)
            denom = 2.0 * a
            t = (-b - e) / denom #smaller root
            if t > 0.00001 and t < min_dist:
                normal = (temp + ray.dir * t) * ( 1.0 / self.radius)
                hit_point = ray.origin + ray.dir * t
                return HitPoint(t, hit_point, normal, self.material, ray)
            
            t = (-b + e) / denom # larger root
            if t > 0.00001 and t < min_dist:
                normal = (temp + ray.dir * t) * (1.0 / self.radius)
                hit_point = ray.origin + ray.dir * t
                return HitPoint(t, hit_point, normal, self.material, ray)
        return False

    def bbox(self):

        epsilon = 0.001
        p0X = self.origin.x - self.radius - epsilon
        p0Y = self.origin.y - self.radius - epsilon
        p0Z = self.origin.z - self.radius - epsilon

        p1X = self.origin.x + self.radius + epsilon
        p1Y = self.origin.y + self.radius + epsilon
        p1Z = self.origin.z + self.radius + epsilon

        p0 = Vector3(p0X, p0Y, p0Z)
        p1 = Vector3(p1X, p1Y, p1Z)

        return BBox(p0, p1, None)


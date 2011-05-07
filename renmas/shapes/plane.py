from .hitpoint import HitPoint

class Plane:
    def __init__(self, point, normal, material):
        self.point = point
        self.normal = normal.normalize()
        self.material = material

    def intersect(self, ray):
        temp = (self.point - ray.origin).dot(self.normal)
        temp2 = ray.dir.dot(self.normal)
        if temp2 == 0.0: return False
        temp3 = temp / temp2
        if temp3 > 0.00001:
            hit_point = ray.origin + ray.dir * temp3
            return HitPoint(temp3, hit_point, self.normal, self.material, ray)
        else:
            return False

    @classmethod
    def intersect_asm(cls, runtime, label_name):
        pass


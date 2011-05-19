
import renmas.utils as util
from .hitpoint import HitPoint

class Triangle:
    def __init__(self, v0, v1, v2, material):
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.material = material
        self.normal = (v1 - v0).cross(v2 - v0)
        self.normal.normalize()

    def intersect(self, ray, min_dist = 999999.0):
        a = self.v0.x - self.v1.x
        b = self.v0.x - self.v2.x
        c = ray.dir.x 
        d = self.v0.x - ray.origin.x
        e = self.v0.y - self.v1.y
        f = self.v0.y - self.v2.y
        g = ray.dir.y
        h = self.v0.y - ray.origin.y
        i = self.v0.z - self.v1.z
        j = self.v0.z - self.v2.z
        k = ray.dir.z
        l = self.v0.z - ray.origin.z


        m = f * k - g * j
        n = h * k - g * l
        p = f * l - h * j
        q = g * i - e * k
        s = e * j - f * i

        inv_denom = 1.0 / (a * m + b * q + c * s)

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

        if t < 0.00001: return False # self-intersection

        hit_point = ray.origin + ray.dir * t

        return HitPoint(t, hit_point, self.normal, self.material, ray)

    def struct_params(self):
        d = {}
        d["p0"] = (self.v0.x, self.v0.y, self.v0.z, 0.0)
        d["p1"] = (self.v1.x, self.v1.y, self.v1.z, 0.0)
        d["p2"] = (self.v2.x, self.v2.y, self.v2.z, 0.0)
        d["normal"] = (self.normal.x, self.normal.y, self.normal.z, 0.0)
        if self.material is None:
            d["mat_index"] = 999999 #TODO try to solve this in better way 
        else:
            d["mat_index"] = self.material
        return d

    @classmethod
    def struct(cls):
        asm_code = """ #DATA
        """
        asm_code += util.structs("triangle") 
        asm_code += """
        #CODE
        #END
        """
        mc = util.get_asm().assemble(asm_code)
        return mc.get_struct("triangle")


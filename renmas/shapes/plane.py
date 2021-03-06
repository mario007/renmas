import random
from .hitpoint import HitPoint
import renmas.utils as util
from renmas.maths import Vector3

class Plane:
    def __init__(self, point, normal, material):
        self.point = point
        self.normal = normal.normalize()
        self.material = material

    def isect(self, ray, min_dist = 999999.0):
        temp = (self.point - ray.origin).dot(self.normal)
        temp2 = ray.dir.dot(self.normal)
        if temp2 == 0.0: return False
        temp3 = temp / temp2
        if temp3 > 0.00001 and temp3 < min_dist:
            hit_point = ray.origin + ray.dir * temp3
            return HitPoint(temp3, hit_point, self.normal, self.material, ray)
        else:
            return False

    @classmethod
    def isect_asm(cls, runtime, label, populate=True):

        asm_structs = util.structs("ray", "plane", "hitpoint")

        ASM = """
        #DATA
        float epsilon = 0.0001
        """
        ASM += asm_structs + """
            ;eax = pointer to ray structure
            ;ebx = pointer to plane structure
            ;ecx = pointer to minimum distance
            ;edx = pointer to hitpoint
        #CODE
        """
        ASM += " global " + label + ":\n" + """
            macro eq128 xmm0 = ebx.plane.normal
            macro dot xmm1 = eax.ray.dir * xmm0 
            macro eq128 xmm2 = ebx.plane.point - eax.ray.origin {xmm0, xmm1}
            macro dot xmm3 = xmm2 * xmm0 {xmm1}
            macro eq32 xmm4 = xmm3 / xmm1

            macro if xmm4 > epsilon goto populate_hitpoint
            mov eax, 0 
            ret
            
            populate_hitpoint:
            ; in ecx is minimum distance
            macro if xmm4 > ecx goto _reject 
        """
        if populate:
            ASM += """
            macro broadcast xmm5 = xmm4[0]
            macro eq128_128 edx.hitpoint.normal = ebx.plane.normal, xmm6 = xmm5 * eax.ray.dir 
            macro eq32 edx.hitpoint.t = xmm4 {xmm6}
            macro eq32_128 edx.hitpoint.mat_index = ebx.plane.mat_index, edx.hitpoint.hit = xmm6 + eax.ray.origin
            """
        ASM += """
            mov eax, 1
            ret

            _reject:
            mov eax, 0
            ret
        """

        assembler = util.get_asm()
        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "ray_plane_isect" + str(util.unique())
        runtime.load(name, mc)

    @classmethod
    def struct(cls):
        asm_code = """ #DATA
        """
        asm_code += util.structs("plane") 
        asm_code += """
        #CODE
        #END
        """
        mc = util.get_asm().assemble(asm_code)
        return mc.get_struct("plane")

    def attributes(self):
        d = {}
        d["point"] = (self.point.x, self.point.y, self.point.z, 0.0)
        d["normal"] = (self.normal.x, self.normal.y, self.normal.z, 0.0)
        if self.material is None:
            d["mat_index"] = 999999 #FIXME - think to solve this in better way
        else:
            d["mat_index"] = self.material
        return d

    @classmethod
    def name(cls):
        return "plane"

    @classmethod
    def isect_name(cls):
        return "ray_plane_intersection"

    def bbox(self):
        raise ValueError("Plane doesn't have BBox for know and mybe never will be one for him!!!")



from .hitpoint import HitPoint
from .bbox import BBox
from ..core import Vector3
from .shape import Shape

class Rectangle(Shape):
    def __init__(self, point, edge_a, edge_b, normal, material):
        self.point = point
        self.edge_a = edge_a
        self.edge_b = edge_b
        self.material = material

        area = edge_a.length() * edge_b.length()
        self.inv_area = 1.0 / area

        self.normal = normal.normalize()
        self.edge_a_squared = edge_a.length_squared()
        self.edge_b_squared = edge_b.length_squared()

    def isect_b(self, ray, min_dist=999999.0): #ray direction must be normalized
        t = (self.point - ray.origin).dot(self.normal) / ray.dir.dot(self.normal)
        if t < 0.00001: return False 
        if t > min_dist: return False

        p = ray.origin + ray.dir * t
        d = p - self.point
        ddota = d.dot(self.edge_a)
        if ddota < 0.0 or ddota > self.edge_a_squared: return False

        ddotb = d.dot(self.edge_b)
        if ddotb < 0.0 or ddotb > self.edge_b_squared: return False

        return t

    # eax = pointer to ray structure
    # ebx = pointer to sphere structure
    # ecx = pointer to minimum distance
    @classmethod
    def isect_asm_b(cls, runtimes, label, assembler, structures):
        code = """
            #DATA
        """
        code += structures.structs(('ray', 'rectangle', 'hitpoint')) + """
        float epsilon = 0.0001
        float zero = 0.0
        #CODE
        """
        code += " global " + label + ":\n" + """
        macro eq128 xmm0 = ebx.rectangle.point - eax.ray.origin 
        macro eq128 xmm1 = ebx.rectangle.normal
        macro dot xmm0 = xmm0 * xmm1 {xmm6, xmm7} 
        macro eq128 xmm2 = eax.ray.dir
        macro dot xmm2 = xmm2 * xmm1 {xmm6, xmm7}
        ; TODO -- think about this macro if xmm2 < epsilon goto _reject
        macro eq32 xmm0 = xmm0 / xmm2 
        ; distance checking
        macro if xmm0 > ecx goto _reject
        macro if xmm0 > epsilon goto _next
        mov eax, 0
        ret

        _next:
        macro broadcast xmm0 = xmm0[0]
        macro eq128 xmm2 = xmm0 * eax.ray.dir + eax.ray.origin 
        macro eq128 xmm3 = xmm2 - ebx.rectangle.point
        macro eq128 xmm4 = ebx.rectangle.edge_a 
        macro dot xmm4 = xmm4 * xmm3  {xmm6, xmm7}
        macro if xmm4 < zero goto _reject
        macro eq32 xmm5 = ebx.rectangle.edge_a_squared
        macro if xmm4 > xmm5 goto _reject
        macro eq128 xmm4 = ebx.rectangle.edge_b 
        macro dot xmm4 = xmm4 * xmm3 {xmm6, xmm7}
        macro if xmm4 < zero goto _reject
        macro eq32 xmm5 = ebx.rectangle.edge_b_squared
        macro if xmm4 > xmm5 goto _reject

        mov eax, 1
        ret

        _reject:
        mov eax, 0
        ret

        """

        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "ray_rectangle_intersection_bool" + str(hash(cls))
        for r in runtimes:
            if not r.global_exists(label):
                r.load(name, mc)


    def isect(self, ray, min_dist = 999999.0):
        t = (self.point - ray.origin).dot(self.normal) / ray.dir.dot(self.normal)
        if t < 0.00001: return False 
        if t > min_dist: return False

        p = ray.origin + ray.dir * t
        d = p - self.point
        ddota = d.dot(self.edge_a)
        if ddota < 0.0 or ddota > self.edge_a_squared: return False

        ddotb = d.dot(self.edge_b)
        if ddotb < 0.0 or ddotb > self.edge_b_squared: return False

        return HitPoint(t, p, self.normal, self.material, ray)

    # eax = pointer to ray structure
    # ebx = pointer to rectangle structure
    # ecx = pointer to minimum distance
    # edx = pointer to hitpoint
    @classmethod
    def isect_asm(cls, runtimes, label, assembler, structures):
        code = """
            #DATA
        """
        code += structures.structs(('ray', 'rectangle', 'hitpoint')) + """
        float epsilon = 0.0001
        float zero = 0.0
        #CODE
        """
        code += " global " + label + ":\n" + """
        macro eq128 xmm0 = ebx.rectangle.point - eax.ray.origin 
        macro eq128 xmm1 = ebx.rectangle.normal
        macro dot xmm0 = xmm0 * xmm1 {xmm6, xmm7} 
        macro eq128 xmm2 = eax.ray.dir
        macro dot xmm2 = xmm2 * xmm1 {xmm6, xmm7}
        ; TODO -- think about this macro if xmm2 < epsilon goto _reject
        macro eq32 xmm0 = xmm0 / xmm2 
        ; distance checking
        macro if xmm0 > ecx goto _reject
        macro if xmm0 > epsilon goto _next
        mov eax, 0
        ret

        _next:
        macro broadcast xmm0 = xmm0[0]
        macro eq128 xmm2 = xmm0 * eax.ray.dir + eax.ray.origin 
        macro eq128 xmm3 = xmm2 - ebx.rectangle.point
        macro eq128 xmm4 = ebx.rectangle.edge_a 
        macro dot xmm4 = xmm4 * xmm3  {xmm6, xmm7}
        macro if xmm4 < zero goto _reject
        macro eq32 xmm5 = ebx.rectangle.edge_a_squared
        macro if xmm4 > xmm5 goto _reject
        macro eq128 xmm4 = ebx.rectangle.edge_b 
        macro dot xmm4 = xmm4 * xmm3 {xmm6, xmm7}
        macro if xmm4 < zero goto _reject
        macro eq32 xmm5 = ebx.rectangle.edge_b_squared
        macro if xmm4 > xmm5 goto _reject

        macro eq128 edx.hitpoint.normal = xmm1 {xmm7}
        macro eq32 edx.hitpoint.t = xmm0 {xmm7}
        macro eq128 edx.hitpoint.hit = xmm2 {xmm7}
        macro eq32 edx.hitpoint.mat_index = ebx.rectangle.mat_index {xmm7}
        mov eax, 1
        ret

        _reject:
        mov eax, 0
        ret

        """

        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "ray_rectangle_intersection" + str(hash(cls))
        for r in runtimes:
            if not r.global_exists(label):
                r.load(name, mc)

    @classmethod
    def name(cls):
        return "rectangle"

    def attributes(self):
        d = {}
        d["point"] = (self.point.x, self.point.y, self.point.z, 0.0)
        d["normal"] = (self.normal.x, self.normal.y, self.normal.z, 0.0)
        d["edge_a"] = (self.edge_a.x, self.edge_a.y, self.edge_a.z, 0.0)
        d["edge_b"] = (self.edge_b.x, self.edge_b.y, self.edge_b.z, 0.0)
        d["edge_a_squared"] = self.edge_a_squared
        d["edge_b_squared"] = self.edge_b_squared
        if self.material is None:
            d["mat_index"] = 999999 #FIXME - think to solve this in better way
        else:
            d["mat_index"] = self.material
        return d

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

        return BBox(p0, p1, None)

    # eax = pointer to hitpoint
    def light_sample(self, runtimes, label, assembler, structures):
        pass



from ..base import Ray
from ..macros import create_assembler
from .hit import HitPoint
from .shape import Shape

class Rectangle(Shape):
    __slots__ = ['point', 'edge_a', 'edge_b', 'normal' ,'material_idx',
            'edge_a_squared', 'edge_b_squared']

    def __init__(self, point, edge_a, edge_b, normal, material_idx=0):
        self.point = point
        self.edge_a = edge_a
        self.edge_b = edge_b
        self.material_idx = material_idx

        self.normal = normal.normalize()
        self.edge_a_squared = edge_a.length_squared()
        self.edge_b_squared = edge_b.length_squared()


    def isect_b(self, ray, min_dist=999999.0): #ray direction must be normalized
        temp1 = ray.dir.dot(self.normal)
        if temp1 == 0.0: return False 

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
    # ebx = pointer to rectangle structure
    # ecx = pointer to minimum distance
    @classmethod
    def isect_asm_b(cls, runtimes, label):
        code = """
            #DATA
        """
        code += Ray.asm_struct() + cls.asm_struct() + """
        float epsilon = 0.0001
        float zero = 0.0
        #CODE
        """
        code += " global " + label + ":\n" + """
        macro eq128 xmm0 = ebx.Rectangle.point - eax.Ray.origin 
        macro eq128 xmm1 = ebx.Rectangle.normal
        macro dot xmm0 = xmm0 * xmm1 {xmm6, xmm7} 
        macro eq128 xmm2 = eax.Ray.dir
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
        macro eq128 xmm2 = xmm0 * eax.Ray.dir + eax.Ray.origin 
        macro eq128 xmm3 = xmm2 - ebx.Rectangle.point
        macro eq128 xmm4 = ebx.Rectangle.edge_a 
        macro dot xmm4 = xmm4 * xmm3  {xmm6, xmm7}
        macro if xmm4 < zero goto _reject
        macro eq32 xmm5 = ebx.Rectangle.edge_a_squared
        macro if xmm4 > xmm5 goto _reject
        macro eq128 xmm4 = ebx.Rectangle.edge_b 
        macro dot xmm4 = xmm4 * xmm3 {xmm6, xmm7}
        macro if xmm4 < zero goto _reject
        macro eq32 xmm5 = ebx.Rectangle.edge_b_squared
        macro if xmm4 > xmm5 goto _reject

        mov eax, 1
        ret

        _reject:
        mov eax, 0
        ret

        """

        assembler = create_assembler()
        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "ray_rectangle_intersection_bool" + str(id(cls))
        for r in runtimes:
            if not r.global_exists(label):
                r.load(name, mc)

    def isect(self, ray, min_dist = 999999.0):
        temp1 = ray.dir.dot(self.normal)
        if temp1 == 0.0: return False 

        t = (self.point - ray.origin).dot(self.normal) / ray.dir.dot(self.normal)
        if t < 0.00001: return False 
        if t > min_dist: return False

        p = ray.origin + ray.dir * t
        d = p - self.point
        ddota = d.dot(self.edge_a)
        if ddota < 0.0 or ddota > self.edge_a_squared: return False

        ddotb = d.dot(self.edge_b)
        if ddotb < 0.0 or ddotb > self.edge_b_squared: return False

        return HitPoint(t, p, self.normal, self.material_idx)


    # eax = pointer to ray structure
    # ebx = pointer to rectangle structure
    # ecx = pointer to minimum distance
    # edx = pointer to hitpoint
    @classmethod
    def isect_asm(cls, runtimes, label):
        code = """
            #DATA
        """
        code += Ray.asm_struct() + cls.asm_struct() + HitPoint.asm_struct() + """
        float epsilon = 0.0001
        float zero = 0.0
        #CODE
        """
        code += " global " + label + ":\n" + """
        macro eq128 xmm0 = ebx.Rectangle.point - eax.Ray.origin 
        macro eq128 xmm1 = ebx.Rectangle.normal
        macro dot xmm0 = xmm0 * xmm1 {xmm6, xmm7} 
        macro eq128 xmm2 = eax.Ray.dir
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
        macro eq128 xmm2 = xmm0 * eax.Ray.dir + eax.Ray.origin 
        macro eq128 xmm3 = xmm2 - ebx.Rectangle.point
        macro eq128 xmm4 = ebx.Rectangle.edge_a 
        macro dot xmm4 = xmm4 * xmm3  {xmm6, xmm7}
        macro if xmm4 < zero goto _reject
        macro eq32 xmm5 = ebx.Rectangle.edge_a_squared
        macro if xmm4 > xmm5 goto _reject
        macro eq128 xmm4 = ebx.Rectangle.edge_b 
        macro dot xmm4 = xmm4 * xmm3 {xmm6, xmm7}
        macro if xmm4 < zero goto _reject
        macro eq32 xmm5 = ebx.Rectangle.edge_b_squared
        macro if xmm4 > xmm5 goto _reject

        macro eq128 edx.Hitpoint.normal = xmm1 {xmm7}
        macro eq32 edx.Hitpoint.t = xmm0 {xmm7}
        macro eq128 edx.Hitpoint.hit = xmm2 {xmm7}
        macro eq32 edx.Hitpoint.material_idx = ebx.Rectangle.material_idx {xmm7}
        mov eax, 1
        ret

        _reject:
        mov eax, 0
        ret

        """

        assembler = create_assembler()
        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "ray_rectangle_intersection" + str(id(cls))
        for r in runtimes:
            if not r.global_exists(label):
                r.load(name, mc)

    def attributes(self):
        d = {}
        d["point"] = self.point.to_ds()
        d["normal"] = self.normal.to_ds()
        d["edge_a"] = self.edge_a.to_ds()
        d["edge_b"] = self.edge_b.to_ds()
        d["edge_a_squared"] = self.edge_a_squared
        d["edge_b_squared"] = self.edge_b_squared
        d["material_idx"] = self.material_idx
        return d

    @classmethod
    def asm_struct_name(cls):
        return "Rectangle"

    @classmethod
    def asm_struct(cls):
        code = """
            struct Rectangle
            float point[4] 
            float normal[4]
            float edge_a[4]
            float edge_b[4]
            float edge_a_squared
            float edge_b_squared
            uint32 material_idx
            end struct
        """
        return code

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

    @classmethod
    def populate_ds(cls, ds, rectangle, name):
        ds[name + '.point'] = rectangle.point.to_ds()
        ds[name + '.normal'] = rectangle.normal.to_ds()
        ds[name + '.edge_a'] = rectangle.edge_a.to_ds()
        ds[name + '.edge_b'] = rectangle.edge_b.to_ds()
        ds[name + '.edge_a_squared'] = rectangle.edge_a_squared
        ds[name + '.edge_b_squared'] = rectangle.edge_b_squared
        ds[name + '.material_idx'] = rectangle.material_idx

    def light_sample(self):
        area = self.edge_a.length() * self.edge_b.length()
        inv_area = 1.0 / area

        code = """
rnd = random2()
shadepoint.shape_pdf = inv_area
shadepoint.shape_normal = normal
shadepoint.shape_sample = point + edge_a * rnd[0] + edge_b * rnd[1]
        """

        props = {'inv_area': inv_area, 'normal': self.normal, 'point': self.point,
                'edge_a': self.edge_a, 'edge_b': self.edge_b}

        return code, props


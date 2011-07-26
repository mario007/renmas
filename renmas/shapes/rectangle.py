
import random
from .hitpoint import HitPoint
from .bbox import BBox
import renmas.utils as util
from renmas.maths import Vector3

class Rectangle:
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

        #asm
        self.sample_ptr = None
        self.ds = None

    def isect(self, ray, min_dist = 999999.0):
        t = (self.point - ray.origin).dot(self.normal) / ray.dir.dot(self.normal)
        #TODO - test if t can be negative!!
        if t < 0.00001: return False 
        if t > min_dist: return False

        p = ray.origin + ray.dir * t
        d = p - self.point
        ddota = d.dot(self.edge_a)
        if ddota < 0.0 or ddota > self.edge_a_squared: return False

        ddotb = d.dot(self.edge_b)
        if ddotb < 0.0 or ddotb > self.edge_b_squared: return False

        return HitPoint(t, p, self.normal, self.material, ray)

    @classmethod
    def isect_asm(cls, runtime, label, populate=True):

        asm_structs = util.structs("ray", "rectangle", "hitpoint")
        ASM = """
        #DATA
        float epsilon = 0.0001
        float zero = 0.0

        """
        ASM += asm_structs + """
            ;eax = pointer to ray structure
            ;ebx = pointer to rectangle structure
            ;ecx = pointer to minimum distance
            ;edx = pointer to hitpoint
        #CODE
        """
        ASM += " global " + label + ":\n" + """
            macro eq128 xmm0 = ebx.rectangle.point - eax.ray.origin 
            macro eq128 xmm1 = ebx.rectangle.normal
            macro dot xmm0 = xmm0 * xmm1 
            macro eq128 xmm2 = eax.ray.dir
            macro dot xmm2 = xmm2 * xmm1 {xmm0}
            macro eq32 xmm0 = xmm0 / xmm2 {xmm1}
            macro if xmm0 > epsilon goto _next
            mov eax, 0
            ret

            _next:
            macro broadcast xmm0 = xmm0[0]
            macro eq128 xmm2 = xmm0 * eax.ray.dir {xmm1}
            macro eq128 xmm2 = xmm2 + eax.ray.origin {xmm0, xmm1}
            macro eq128 xmm3 = xmm2 - ebx.rectangle.point {xmm0, xmm1}
            macro eq128 xmm4 = ebx.rectangle.edge_a {xmm0, xmm1, xmm2, xmm3} 
            macro dot xmm4 = xmm4 * xmm3  {xmm0, xmm1, xmm2}
            macro if xmm4 < zero goto _reject
            macro eq32 xmm5 = ebx.rectangle.edge_a_squared {xmm0, xmm1, xmm2, xmm3}
            macro if xmm4 > xmm5 goto _reject
            macro eq128 xmm4 = ebx.rectangle.edge_b {xmm0, xmm1, xmm2, xmm3} 
            macro dot xmm4 = xmm4 * xmm3  {xmm0, xmm1, xmm2}
            macro if xmm4 < zero goto _reject
            macro eq32 xmm5 = ebx.rectangle.edge_b_squared {xmm0, xmm1, xmm2, xmm3}
            macro if xmm4 > xmm5 goto _reject

            ; distance checking
            macro if xmm0 > ecx goto _reject
        """
        if populate:
            ASM += """
                macro eq128 edx.hitpoint.normal = xmm1
                macro eq32 edx.hitpoint.t = xmm0
                macro eq128 edx.hitpoint.hit = xmm2
                macro eq32 edx.hitpoint.mat_index = ebx.rectangle.mat_index
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
        name = "ray_rectangle_isect" + str(util.unique())
        runtime.load(name, mc)

    def light_sample(self, hitpoint):
        hitpoint.light_pdf = self.inv_area
        hitpoint.light_normal = self.normal

        r1 = random.random()
        r2 = random.random()
        hitpoint.light_sample = self.point + self.edge_a * r1 + self.edge_b * r2

    def light_sample_asm(self, runtime):
        util.load_func(runtime, "random")
        #eax - pointer to hitpoint structure
        asm_structs = util.structs("hitpoint")
        ASM = """
        #DATA
        """
        ASM += asm_structs + """
        float normal[4]
        float edge_a[4]
        float edge_b[4]
        float point[4]
        float pdf
        uint32 hp_ptr
        #CODE
        mov dword [hp_ptr], eax
        call random
        macro eq128 xmm1 = xmm0
        macro broadcast xmm0 = xmm0[0] 
        macro broadcast xmm1 = xmm1[1]
        macro eq128 xmm0 = xmm0 * edge_a {xmm1}
        macro eq128 xmm1 = xmm1 * edge_b {xmm0}
        macro eq128 xmm0 = xmm0 + point {xmm1}
        macro eq128 xmm0 = xmm0 + xmm1 
        mov eax, dword [hp_ptr]
        macro eq128 eax.hitpoint.light_sample = xmm0
        macro eq128 eax.hitpoint.light_normal = normal
        macro eq32 eax.hitpoint.light_pdf = pdf
        ret
        
        """
        assembler = util.get_asm()
        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "recangle_sample" + str(util.unique())

        self.ds = runtime.load(name, mc)
        self._populate_ds()

        #FIXME - add method to runtime class so we can ask runtime for address of module
        self.sample_ptr = runtime.modules[name][0]

    def _populate_ds(self):
        if self.ds is None: return
        p = self.point
        self.ds["point"] = (p.x, p.y, p.z, 0.0)
        e = self.edge_a
        self.ds["edge_a"] = (e.x, e.y, e.z, 0.0)
        e = self.edge_b
        self.ds["edge_b"] = (e.x, e.y, e.z, 0.0)
        n = self.normal
        self.ds["normal"] = (n.x, n.y, n.z, 0.0)
        self.ds["pdf"] = self.inv_area

    @classmethod
    def name(cls):
        return "rectangle"

    @classmethod
    def isect_name(cls):
        return "ray_rectangle_intersection"

    def bbox(self):
        raise ValueError("Rectangle doesn't have BBox yet!!!")

    @classmethod
    def struct(cls):
        asm_code = """ #DATA
        """
        asm_code += util.structs("rectangle") 
        asm_code += """
        #CODE
        #END
        """
        mc = util.get_asm().assemble(asm_code)
        return mc.get_struct("rectangle")

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


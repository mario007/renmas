
import unittest
from random import random
from tdasm import Runtime
import renmas2

class RectangleIsectTest(unittest.TestCase):
    def setUp(self):
        self.counter = 0

    def ray_ds(self, ds, ray, name):
        o = ray.origin
        d = ray.dir
        ds[name+ ".origin"] = (o.x, o.y, o.z, 0.0)
        ds[name+ ".dir"] = (d.x, d.y, d.z, 0.0)

    def rectangle_ds(self, ds, rectangle, name):
        p = rectangle.point
        ds[name+ ".point"] = (p.x, p.y, p.z, 0.0)
        n = rectangle.normal
        ds[name+ ".normal"] = (n.x, n.y, n.z, 0.0)
        e1 = rectangle.edge_a
        ds[name+ ".edge_a"] = (e1.x, e1.y, e1.z, 0.0)
        e2 = rectangle.edge_b
        ds[name+ ".edge_b"] = (e2.x, e2.y, e2.z, 0.0)
        ds[name + ".edge_a_squared"] = rectangle.edge_a_squared
        ds[name + ".edge_b_squared"] = rectangle.edge_b_squared

    def compare_seq(self, sq1, sq2):
        for i in range(len(sq1)):
            self.assertAlmostEqual(sq1[i], sq2[i], 3)

    def compare(self, hp, ds, name, ray, rectangle):
        self.counter += 1

        t1 = hp.t 
        t2 = ds[name + ".t"]
        #msg = "\n" + str(ray) + "\n" + str(sphere) 
        msg = "\n" + str(ray) + "\n"
        self.assertAlmostEqual(t1, t2, 4, msg)
        n1 = hp.normal
        n2 = ds[name + ".normal"]
        self.compare_seq((n1.x, n1.y, n1.z), (n2[0], n2[1], n2[2]))
        hit1 = hp.hit_point
        hit2 = ds[name + ".hit"]
        self.compare_seq((hit1.x, hit1.y, hit1.z), (hit2[0], hit2[1], hit2[2]))

    def asm_code(self, ren):
        code = """
            #DATA
        """
        code += ren.structures.structs(('ray', 'rectangle', 'hitpoint')) + """
            ray ray1
            rectangle rec1
            hitpoint hp1
            float min_dist = 99999.000
            uint32 ret

            #CODE
            mov eax, ray1
            mov ebx, rec1 
            mov ecx, min_dist
            mov edx, hp1
            call ray_rectangle_intersection 
            mov dword [ret], eax

            #END
        """
        return code

    def intersect(self, ray, rectangle, runtime, ds):
        self.ray_ds(ds, ray, "ray1")
        self.rectangle_ds(ds, rectangle, "rec1")
        runtime.run("test")
        hp = rectangle.isect(ray)

        if hp is False: self.assertFalse(ds["ret"]!=0)
        if ds["ret"] == 0: self.assertFalse(hp)
        if hp is not False:
            self.compare(hp, ds, "hp1", ray, rectangle)

    def test_isect1(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()

        rectangle = factory.create_rectangle(point=(0,0,55.92), e1=(55.28,0,0), e2=(0,54.88,0.0), normal=(0.0,0.0,-1.0))
        ray = factory.create_ray(origin=(3,2.5,0), direction=(0,0.1,0.88))
        hp = rectangle.isect(ray)

        rectangle.isect_asm([runtime], "ray_rectangle_intersection", ren.assembler, ren.structures)
        mc = ren.assembler.assemble(self.asm_code(ren))
        ds = runtime.load("test", mc)

        self.intersect(ray, rectangle, runtime, ds)

if __name__ == "__main__":
    unittest.main()


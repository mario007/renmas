
import unittest
from random import random
from tdasm import Runtime
import renmas2

class TriangleIsectTest(unittest.TestCase):
    def setUp(self):
        self.counter = 0

    def ray_ds(self, ds, ray, name):
        o = ray.origin
        d = ray.dir
        ds[name+ ".origin"] = (o.x, o.y, o.z, 0.0)
        ds[name+ ".dir"] = (d.x, d.y, d.z, 0.0)

    def triangle_ds(self, ds, triangle, name):
        v0 = triangle.v0
        ds[name+".v0"] = (v0.x, v0.y, v0.z, 0.0) 
        v1 = triangle.v1
        ds[name+".v1"] = (v1.x, v1.y, v1.z, 0.0) 
        v2 = triangle.v2
        ds[name+".v2"] = (v2.x, v2.y, v2.z, 0.0) 
        if triangle.has_normals:
            n0 = triangle.n0
            ds[name+".n0"] = (n0.x, n0.y, n0.z, 0.0) 
            n1 = triangle.n1
            ds[name+".n1"] = (n1.x, n1.y, n1.z, 0.0) 
            n2 = triangle.n2
            ds[name+".n2"] = (n2.x, n2.y, n2.z, 0.0) 
        else:
            n = triangle.normal
            ds[name+".normal"] = (n.x, n.y, n.z, 0.0) 

        if triangle.material:
            ds[name+".mat_index"] = triangle.material

    def random_ray(self):
        factory = renmas2.Factory()
        origin = (random(), random(), random())
        direction = (random(), random(), random())
        return factory.create_ray(origin, direction)

    def random_triangle(self):
        factory = renmas2.Factory()
        v0 = (random(), random(), random())
        v1 = (random(), random(), random())
        v2 = (random(), random(), random())
        triangle = factory.create_triangle(v0=v0, v1=v1, v2=v2)
        return triangle

    def compare_seq(self, sq1, sq2):
        for i in range(len(sq1)):
            self.assertAlmostEqual(sq1[i], sq2[i], 3)

    def compare(self, hp, ds, name, ray, triangle):
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


    def intersect(self, ray, triangle, runtime, ds):
        self.ray_ds(ds, ray, "ray1")
        self.triangle_ds(ds, triangle, "tri1")
        runtime.run("test")
        hp = triangle.isect(ray)

        if hp is False: self.assertFalse(ds["ret"]!=0)
        if ds["ret"] == 0: self.assertFalse(hp)
        if hp is not False:
            self.compare(hp, ds, "hp1", ray, triangle)

    def asm_code(self, ren):
        code = """
            #DATA
        """
        code += ren.structures.structs(('ray', 'triangle', 'hitpoint')) + """
            ray ray1
            triangle tri1
            hitpoint hp1
            float min_dist = 99999.000
            uint32 ret

            #CODE
            mov eax, ray1
            mov ebx, tri1 
            mov ecx, min_dist
            mov edx, hp1
            call ray_triangle_intersection 
            mov dword [ret], eax

            #END
        """
        return code

    def test_isect1(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()

        triangle = factory.create_triangle(v0=(2,2,2), v1=(5,2,2), v2=(3.5,5,2))
        ray = factory.create_ray(origin=(3,2.5,0), direction=(0,0.1,0.88))
        hp = triangle.isect(ray)

        triangle.isect_asm([runtime], "ray_triangle_intersection", ren.assembler, ren.structures)
        mc = ren.assembler.assemble(self.asm_code(ren))
        ds = runtime.load("test", mc)

        self.ray_ds(ds, ray, "ray1")
        self.triangle_ds(ds, triangle, "tri1")
        runtime.run("test")
        self.intersect(ray, triangle, runtime, ds)
        for i in range(1000):
            r = self.random_ray()
            t = self.random_triangle()
            self.intersect(r, t, runtime, ds)
        #print (self.counter)

    def asm_code2(self, ren):
        code = """
            #DATA
        """
        code += ren.structures.structs(('ray', 'triangle', 'hitpoint')) + """
            ray ray1
            triangle tri1
            float min_dist = 99999.000
            uint32 ret
            float t
            #CODE
            mov eax, ray1
            mov ebx, tri1
            mov ecx, min_dist
            call ray_sphere_intersection 
            mov dword [ret], eax
            macro eq32 t = xmm0 {xmm0}
            #END
        """
        return code

    def intersect2(self, ray, triangle, runtime, ds):
        self.ray_ds(ds, ray, "ray1")
        self.triangle_ds(ds, triangle, "tri1")
        runtime.run("test")
        hp = triangle.isect_b(ray)

        if hp is False: self.assertFalse(ds["ret"]!=0)
        if ds["ret"] == 0: self.assertFalse(hp)
        if hp is not False:
            t2 = ds["t"]
            self.assertAlmostEqual(hp, t2, 4)

    def test_isect2(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()
        triangle = factory.create_triangle(v0=(2,2,2), v1=(5,2,2), v2=(3.5,5,2))
        ray = factory.create_ray(origin=(3,2.5,0), direction=(0,0.1,0.88))

        triangle.isect_asm_b([runtime], "ray_sphere_intersection", ren.assembler, ren.structures)
        mc = ren.assembler.assemble(self.asm_code2(ren))
        ds = runtime.load("test", mc)

        self.intersect2(ray, triangle, runtime, ds)
        for i in range(10000):
            r = self.random_ray()
            t = self.random_triangle()
            self.intersect2(r, t, runtime, ds)


if __name__ == "__main__":
    unittest.main()


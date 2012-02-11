
import unittest
from random import random
from tdasm import Runtime
import renmas2

class LinearIsectTest(unittest.TestCase):
    def setUp(self):
        pass

    def add_rnd_sphere(self, ren):
        factory = renmas2.Factory()
        origin = (random(), random(), random())
        radius = random()
        sph = factory.create_sphere(origin, radius)
        ren.add("sphere" + str(hash(sph)), sph)

    def add_rnd_triangle(self, ren):
        factory = renmas2.Factory()
        v0 = (random()*5, random()*5, random()*5)
        v1 = (random(), random(), random()*5)
        v2 = (random()*10, random(), random()*5)
        triangle = factory.create_triangle(v0=v0, v1=v1, v2=v2)
        ren.add("triangle" + str(hash(triangle)), triangle)

    def random_ray(self):
        factory = renmas2.Factory()
        origin = (random()*10, random(), random()*10)
        direction = (random(), random(), random())
        return factory.create_ray(origin, direction)

    def ray_ds(self, ds, ray, name):
        o = ray.origin
        d = ray.dir
        ds[name+ ".origin"] = (o.x, o.y, o.z, 0.0)
        ds[name+ ".dir"] = (d.x, d.y, d.z, 0.0)

    def asm_code(self, ren):
        # eax - ray
        # ebx - hitpoint
        code = """
            #DATA
        """
        code += ren.structures.structs(('ray', 'sphere', 'hitpoint')) + """
            ray ray1
            hitpoint hp1
            uint32 ret

            #CODE
            mov eax, ray1
            mov ebx, hp1
            call ray_scene_intersection
            mov dword [ret], eax
            #END
        """
        return code

    def compare_seq(self, sq1, sq2):
        for i in range(len(sq1)):
            self.assertAlmostEqual(sq1[i], sq2[i], 3)

    def compare(self, hp, ds, name, ray):
        t1 = hp.t 
        t2 = ds[name + ".t"]
        self.assertAlmostEqual(t1, t2, 4)
        n1 = hp.normal
        n2 = ds[name + ".normal"]
        self.compare_seq((n1.x, n1.y, n1.z), (n2[0], n2[1], n2[2]))
        hit1 = hp.hit_point
        hit2 = ds[name + ".hit"]
        self.compare_seq((hit1.x, hit1.y, hit1.z), (hit2[0], hit2[1], hit2[2]))

    def intersect(self, ray, runtime, ds, intersector):
        self.ray_ds(ds, ray, "ray1")
        runtime.run("test")
        hp = intersector.isect(ray)

        if hp is False: self.assertFalse(ds["ret"]!=0)
        if ds["ret"] == 0: self.assertFalse(hp)
        if hp is not False:
            self.compare(hp, ds, "hp1", ray)

    def test_linear1(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()
        
        for i in range(100):
            self.add_rnd_sphere(ren)
            self.add_rnd_triangle(ren)

        ren.prepare()
        ren.intersector.isect_asm([runtime], "ray_scene_intersection")
        mc = ren.assembler.assemble(self.asm_code(ren))
        ds = runtime.load("test", mc)

        ray = self.random_ray()
        for i in range(1000):
            ray = self.random_ray()
            self.intersect(ray, runtime, ds, ren.intersector)

    def asm_code2(self, ren):
        # eax - ray
        # ebx - hitpoint
        code = """
            #DATA
            float p1[4]
            float p2[4]
            uint32 ret

            #CODE
            macro eq128 xmm0 = p1
            macro eq128 xmm1 = p2
            call ray_scene_visibility
            mov dword [ret], eax
            #END
        """
        return code

    def intersect2(self, runtime, ds, intersector, p1, p2):
        ds["p1"] = (p1.x, p1.y, p1.z, 0.0)
        ds["p2"] = (p2.x, p2.y, p2.z, 0.0)
        runtime.run("test")
        t = intersector.visibility(p1, p2)

        if t is False: self.assertFalse(ds["ret"]!=0)
        if ds["ret"] == 0: self.assertFalse(t)

    def test_visibility1(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()
        
        for i in range(2):
            self.add_rnd_sphere(ren)

        ren.prepare()
        ren.intersector.visibility_asm([runtime], "ray_scene_visibility")
        mc = ren.assembler.assemble(self.asm_code2(ren))
        ds = runtime.load("test", mc)

        p1 = renmas2.Vector3(random(), random(), random())
        p2 = renmas2.Vector3(random(), random(), random())
        self.intersect2(runtime, ds, ren.intersector, p1, p2)


if __name__ == "__main__":
    unittest.main()



import unittest
from random import random
from tdasm import Runtime
import renmas2

class SphereIsectTest(unittest.TestCase):
    def setUp(self):
        self.counter = 0

    def ray_ds(self, ds, ray, name):
        o = ray.origin
        d = ray.dir
        ds[name+ ".origin"] = (o.x, o.y, o.z, 0.0)
        ds[name+ ".dir"] = (d.x, d.y, d.z, 0.0)

    def sphere_ds(self, ds, sphere, name):
        o = sphere.origin
        ds[name+".origin"] = (o.x, o.y, o.z, 0.0) 
        ds[name+".radius"] = sphere.radius
        ds[name+".mat_index"] = sphere.material

    def asm_code(self, ren):
        code = """
            #DATA
        """
        code += ren.structures.structs(('ray', 'sphere', 'hitpoint')) + """
            ray ray1
            sphere sph1
            hitpoint hp1
            float min_dist = 99999.000
            uint32 ret
            #CODE
            mov eax, ray1
            mov ebx, sph1
            mov ecx, min_dist
            mov edx, hp1
            call ray_sphere_intersection 
            mov dword [ret], eax
            #END
        """
        return code

    def compare_seq(self, sq1, sq2):
        for i in range(len(sq1)):
            self.assertAlmostEqual(sq1[i], sq2[i], 3)

    def compare(self, hp, ds, name, ray, sphere):
        self.counter += 1

        t1 = hp.t 
        t2 = ds[name + ".t"]
        msg = "\n" + str(ray) + "\n" + str(sphere) 
        self.assertAlmostEqual(t1, t2, 4, msg)
        n1 = hp.normal
        n2 = ds[name + ".normal"]
        self.compare_seq((n1.x, n1.y, n1.z), (n2[0], n2[1], n2[2]))
        hit1 = hp.hit_point
        hit2 = ds[name + ".hit"]
        self.compare_seq((hit1.x, hit1.y, hit1.z), (hit2[0], hit2[1], hit2[2]))


    def random_sphere(self):
        factory = renmas2.Factory()
        origin = (random(), random(), random())
        radius = random()
        return factory.create_sphere(origin, radius)

    def random_ray(self):
        factory = renmas2.Factory()
        origin = (random(), random(), random())
        direction = (random(), random(), random())
        return factory.create_ray(origin, direction)

    def intersect(self, ray, sphere, runtime, ds):
        self.ray_ds(ds, ray, "ray1")
        self.sphere_ds(ds, sphere, "sph1")
        runtime.run("test")
        hp = sphere.isect(ray)

        if hp is False: self.assertFalse(ds["ret"]!=0)
        if ds["ret"] == 0: self.assertFalse(hp)
        if hp is not False:
            self.compare(hp, ds, "hp1", ray, sphere)

    def test_isect1(self):
        factory = renmas2.Factory()
        ray = factory.create_ray(origin=(5,5,5), direction=(-1,-1,-1))
        sphere = factory.create_sphere(origin=(0,0,0), radius=2)
        ren = renmas2.Renderer()
        runtime = Runtime()
        sphere.isect_asm([runtime], "ray_sphere_intersection", ren.assembler, ren.structures)
        mc = ren.assembler.assemble(self.asm_code(ren))
        ds = runtime.load("test", mc)

        self.intersect(ray, sphere, runtime, ds)
        for i in range(10000):
            r = self.random_ray()
            s = self.random_sphere()
            self.intersect(r, s, runtime, ds)

    def asm_code2(self, ren):
        code = """
            #DATA
        """
        code += ren.structures.structs(('ray', 'sphere', 'hitpoint')) + """
            ray ray1
            sphere sph1
            float min_dist = 99999.000
            uint32 ret
            float t
            #CODE
            mov eax, ray1
            mov ebx, sph1
            mov ecx, min_dist
            call ray_sphere_intersection 
            mov dword [ret], eax
            macro eq32 t = xmm0 {xmm0}
            #END
        """
        return code

    def intersect2(self, ray, sphere, runtime, ds):
        self.ray_ds(ds, ray, "ray1")
        self.sphere_ds(ds, sphere, "sph1")
        runtime.run("test")
        hp = sphere.isect_b(ray)

        if hp is False: self.assertFalse(ds["ret"]!=0)
        if ds["ret"] == 0: self.assertFalse(hp)
        if hp is not False:
            t2 = ds["t"]
            self.assertAlmostEqual(hp, t2, 4)

    def test_isect2(self):
        factory = renmas2.Factory()
        ray = factory.create_ray(origin=(5,5,5), direction=(-1,-1,-1))
        sphere = factory.create_sphere(origin=(0,0,0), radius=2)
        ren = renmas2.Renderer()
        runtime = Runtime()
        sphere.isect_asm_b([runtime], "ray_sphere_intersection", ren.assembler, ren.structures)
        mc = ren.assembler.assemble(self.asm_code2(ren))
        ds = runtime.load("test", mc)

        self.intersect2(ray, sphere, runtime, ds)
        for i in range(10000):
            r = self.random_ray()
            s = self.random_sphere()
            self.intersect2(r, s, runtime, ds)

if __name__ == "__main__":
    unittest.main()



import unittest
from random import random
from tdasm import Runtime
from renmas3.base import Vector3, Ray
from renmas3.shapes import HitPoint, Sphere
from renmas3.macros import create_assembler

class SphereIsectTest(unittest.TestCase):
    def setUp(self):
        self.counter = 0

    def ray_ds(self, ds, ray, name):
        ds[name+ ".origin"] = ray.origin.to_ds() 
        ds[name+ ".dir"] = ray.dir.to_ds()

    def sphere_ds(self, ds, sphere, name):
        ds[name+".origin"] =  sphere.origin.to_ds()
        ds[name+".radius"] = sphere.radius
        ds[name+".material_idx"] = sphere.material_idx

    def asm_code(self):
        code = """
            #DATA
        """
        code += Ray.asm_struct() + Sphere.asm_struct() + HitPoint.asm_struct() + """
            Ray ray1
            Sphere sph1
            Hitpoint hp1
            float min_dist = 99999.000
            uint32 ret
            #CODE
            macro mov eax, ray1
            macro mov ebx, sph1
            macro mov ecx, min_dist
            macro mov edx, hp1
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
        hit1 = hp.hit
        hit2 = ds[name + ".hit"]
        self.compare_seq((hit1.x, hit1.y, hit1.z), (hit2[0], hit2[1], hit2[2]))

    def random_sphere(self):
        origin = Vector3(random(), random(), random())
        radius = random()
        return Sphere(origin, radius)

    def random_ray(self):
        origin = Vector3(random(), random(), random())
        direction = Vector3(random(), random(), random())
        direction.normalize()
        return Ray(origin, direction)

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
        direction = Vector3(-1.0, -1.0, -1.0)
        direction.normalize()
        ray = Ray(Vector3(5.0, 5.0, 5.0), direction)
        sphere = Sphere(Vector3(0.0, 0.0, 0.0), 2)

        runtime = Runtime()
        assembler = create_assembler()
        sphere.isect_asm([runtime], "ray_sphere_intersection")
        mc = assembler.assemble(self.asm_code())
        ds = runtime.load("test", mc)

        self.intersect(ray, sphere, runtime, ds)
        for i in range(100):
            r = self.random_ray()
            s = self.random_sphere()
            self.intersect(r, s, runtime, ds)

    def asm_code2(self):
        code = """
            #DATA
        """
        code += Ray.asm_struct() + Sphere.asm_struct() + """
            Ray ray1
            Sphere sph1
            float min_dist = 99999.000
            uint32 ret
            float t
            #CODE
            macro mov eax, ray1
            macro mov ebx, sph1
            macro mov ecx, min_dist
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
        direction = Vector3(-1.0, -1.0, -1.0)
        direction.normalize()
        ray = Ray(Vector3(5.0, 5.0, 5.0), direction)
        sphere = Sphere(Vector3(0.0, 0.0, 0.0), 2)


        runtime = Runtime()
        assembler = create_assembler()
        sphere.isect_asm_b([runtime], "ray_sphere_intersection")
        mc = assembler.assemble(self.asm_code2())
        ds = runtime.load("test", mc)

        self.intersect2(ray, sphere, runtime, ds)
        for i in range(10000):
            r = self.random_ray()
            s = self.random_sphere()
            self.intersect2(r, s, runtime, ds)

if __name__ == "__main__":
    unittest.main()


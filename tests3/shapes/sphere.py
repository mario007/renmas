
import unittest
from random import random
from tdasm import Runtime
from renmas3.core.structures import RAY, SPHERE, SHADEPOINT
from renmas3.core import Factory, ColorManager

class SphereIsectTest(unittest.TestCase):
    def setUp(self):
        self.counter = 0

    def ray_ds(self, ds, ray, name):
        ds[name+ ".origin"] = ray.origin.to_ds() 
        ds[name+ ".dir"] = ray.dir.to_ds()

    def sphere_ds(self, ds, sphere, name):
        ds[name+".origin"] =  sphere.origin.to_ds()
        ds[name+".radius"] = sphere.radius
        #TODO -- test this if material is None -- fix this in assembler - raise exception
        ds[name+".material"] = sphere.material

    def asm_code(self, spec_struct):
        code = """
            #DATA
        """
        code += spec_struct + RAY + SPHERE + SHADEPOINT + """
            ray ray1
            sphere sph1
            shadepoint hp1
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
        factory = Factory()
        origin = (random(), random(), random())
        radius = random()
        return factory.sphere(origin, radius)

    def random_ray(self):
        factory = Factory()
        origin = (random(), random(), random())
        direction = (random(), random(), random())
        return factory.ray(origin, direction)

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
        factory = Factory()
        ray = factory.ray(origin=(5,5,5), direction=(-1,-1,-1))
        sphere = factory.sphere(origin=(0,0,0), radius=2)

        mgr = ColorManager()
        runtime = Runtime()
        sphere.isect_asm([runtime], "ray_sphere_intersection", mgr.assembler, mgr.spectrum_struct())
        mc = mgr.assembler.assemble(self.asm_code(mgr.spectrum_struct()))
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
        code += RAY + SPHERE + """
            ray ray1
            sphere sph1
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
        factory = Factory()
        ray = factory.ray(origin=(5,5,5), direction=(-1,-1,-1))
        sphere = factory.sphere(origin=(0,0,0), radius=2)
        mgr = ColorManager() 
        runtime = Runtime()
        sphere.isect_asm_b([runtime], "ray_sphere_intersection", mgr.assembler)
        mc = mgr.assembler.assemble(self.asm_code2())
        ds = runtime.load("test", mc)

        self.intersect2(ray, sphere, runtime, ds)
        for i in range(10000):
            r = self.random_ray()
            s = self.random_sphere()
            self.intersect2(r, s, runtime, ds)

if __name__ == "__main__":
    unittest.main()


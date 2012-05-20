import time
import unittest
from random import random
from tdasm import Runtime
import renmas2

class IsectTest(unittest.TestCase):
    def setUp(self):
        pass

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

    def test_isect(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()
        irender = renmas2.IRender(ren)
        filename = 'C:\\Users\\Mario\\Desktop\\glass\\glass.py'
        exec(compile(open(filename).read(), filename, 'exec'), dict(locals()), dict(globals()))

        ren.prepare()

        ren.macro_call.set_runtimes([runtime])
        ren.intersector.isect_asm([runtime], 'ray_scene_intersection')
        mc = ren.assembler.assemble(self.asm_code(ren))
        ds = runtime.load("test", mc)

        camera = ren.camera
        sampler = ren.sampler

        for tile in ren._tiles3:
            sampler.set_tile(tile)

            while True:
                sam = sampler.get_sample()
                if sam is None: break
                ray = camera.ray(sam)
                self.ray_ds(ds, ray, "ray1")
                runtime.run("test")
                t = ds["hp1.t"]
                hp = ren.intersector.isect(ray) 
                if hp is False: self.assertFalse(ds["ret"]!=0)
                if ds["ret"] == 0: self.assertFalse(hp)

                if hp is not False:
                    n1 = hp.normal
                    n2 = ds["hp1.normal"]
                    #print("Normal")
                    #print(n1)
                    #print(n2)
                    #print("Hit point")
                    #print(hp.hit_point)
                    #print(ds['hp1.hit'])
                    
                    self.assertAlmostEqual(hp.t, t, 1)
                    print(t, hp.t)
                    print(n1)
                    print(n2)


                    self.assertAlmostEqual(n1.x, n2[0], 1)
                    self.assertAlmostEqual(n1.y, n2[1], 1)
                    self.assertAlmostEqual(n1.z, n2[2], 1)


if __name__ == "__main__":
    unittest.main()



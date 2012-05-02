import time
import unittest
from random import random
from tdasm import Runtime
import renmas2

class GridPerformanceTest(unittest.TestCase):
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
            uint32 counter1, counter2, counter3
            float tx_next
            float ty_next
            float tz_next

            #CODE
            mov eax, ray1
            mov ebx, hp1
            call ray_scene_intersection
            mov dword [ret], eax
            mov dword [counter1], ebx
            mov dword [counter2], ecx
            mov dword [counter3], edx
            macro eq32 tx_next = xmm5 {xmm0}
            macro eq32 ty_next = xmm6 {xmm0}
            macro eq32 tz_next = xmm7 {xmm0}
            #END
        """
        return code

    def test_grid_performance(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()
        irender = renmas2.IRender(ren)
        filename = 'G:\\GitRENMAS\\renmas\\scenes\\mini_moris.py'
        exec(compile(open(filename).read(), filename, 'exec'), dict(locals()), dict(globals()))

        ren.prepare()

        ren.macro_call.set_runtimes([runtime])
        ren.intersector.isect_asm([runtime], 'ray_scene_intersection')
        mc = ren.assembler.assemble(self.asm_code(ren))
        ds = runtime.load("test", mc)

        ren.sampler.set_tile(ren._tiles3[0])
        while True:
            sam = ren.sampler.get_sample()
            if sam is None: break 
            if sam.iy == 105:
                if sam.ix == 188:
                    ray = ren.camera.ray(sam) 
                    self.ray_ds(ds, ray, "ray1")
                    start = time.clock()
                    runtime.run("test")
                    end = time.clock() - start
                    print ("Time:", end)
                    print ("Counter1", ds["counter1"])
                    print ("Counter2", ds["counter2"])
                    print ("Counter3", ds["counter3"])
                    print ("tx_next", ds["tx_next"])
                    print ("ty_next", ds["ty_next"])
                    print ("tz_next", ds["tz_next"])
                    break

        hp = ren.intersector.isect(ray) 
        if hp:
            print("intersection ocur")
        else:
            print("no intersection ocur")

if __name__ == "__main__":
    unittest.main()


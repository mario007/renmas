
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

    def asm_code(self, ren):
        code = """
            #DATA
        """
        code += ren.structures.structs(('ray', 'hitpoint')) + """ 
            ray ray1
            hitpoint hp1
            uint32 ret
            uint32 addr

            #CODE
            mov eax, ray1
            mov ebx, hp1
            call ray_scene_intersection 
            mov dword [ret], eax
            mov dword [addr], edi

            #END
        """

        return code

    def test_isect1(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()
        irender = renmas2.IRender(ren)
        #irender.add_shape(type="mesh", name="cube1", filename="I:/Ply_files/Horse97K.ply")
        #irender.add_shape(type="mesh", name="cube1", filename="I:/Obj_files/auto1.obj")

        triangle = factory.create_triangle(v0=(2,2,2), v1=(5,2,2), v2=(3.5,5,2))
        ray = factory.create_ray(origin=(3,2.5,0), direction=(0,0.1,0.88))
        ren.add("triangle1", triangle)

        ray = factory.create_ray(origin=(10,10,10), direction=(-1,-1,-1))

        ren.intersector.prepare()
        ren.intersector.isect_asm([runtime], "ray_scene_intersection")
        mc = ren.assembler.assemble(self.asm_code(ren))
        ds = runtime.load("test", mc)

        ren.intersector.visibility_asm([runtime], "ray_scene_intersection_bool")
        
        self.ray_ds(ds, ray, "ray1")

        runtime.run("test")
        print(ds["hp1.t"])

        hp = ren.intersector.isect(ray)
        print(hp.t)

        #hp1 = triangle.isect(ray)
        #print(hp1.t)

if __name__ == "__main__":
    unittest.main()



import unittest
from random import random
from tdasm import Runtime
from renmas3.base import Ray, Vector3
from renmas3.shapes import Rectangle, HitPoint
from renmas3.macros import create_assembler

class RectangleIsectTest(unittest.TestCase):
    def setUp(self):
        self.counter = 0

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
        hit1 = hp.hit
        hit2 = ds[name + ".hit"]
        self.compare_seq((hit1.x, hit1.y, hit1.z), (hit2[0], hit2[1], hit2[2]))

    def asm_code(self):
        code = """
            #DATA
        """
        code += Ray.asm_struct() + Rectangle.asm_struct() + HitPoint.asm_struct() + """
            Ray ray1
            Rectangle rec1
            Hitpoint hp1
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

    def asm_code_bool(self):
        code = """
            #DATA
        """
        code += Ray.asm_struct() + Rectangle.asm_struct() + """
            Ray ray1
            Rectangle rec1
            float min_dist = 99999.000
            uint32 ret

            #CODE
            macro mov eax, ray1
            macro mov ebx, rec1 
            macro mov ecx, min_dist
            call ray_rectangle_intersection 
            mov dword [ret], eax

            #END
        """
        return code

    def intersect(self, ray, rectangle, runtime, ds):
        Ray.populate_ds(ds, ray, 'ray1')
        Rectangle.populate_ds(ds, rectangle, 'rec1')

        runtime.run("test")
        hp = rectangle.isect(ray)

        if hp is False: self.assertFalse(ds["ret"]!=0)
        if ds["ret"] == 0: self.assertFalse(hp)
        if hp is not False:
            self.compare(hp, ds, "hp1", ray, rectangle)

    def test_isect1(self):
        point = Vector3(0.0, 0.0, 55.92)
        e1 = Vector3(55.28, 0.0, 0.0)
        e2 = Vector3(0.0, 54.88, 0.0)
        normal = Vector3(0.0, 0.0, -1.0)
        rectangle = Rectangle(point, e1, e2, normal)

        origin = Vector3(3.0, 2.5, 0.0)
        direction = Vector3(0.0, 0.1, 0.88)
        direction.normalize()
        ray = Ray(origin, direction)

        runtime = Runtime()
        rectangle.isect_asm([runtime], "ray_rectangle_intersection")

        assembler = create_assembler()
        mc = assembler.assemble(self.asm_code())
        ds = runtime.load("test", mc)

        self.intersect(ray, rectangle, runtime, ds)

    def test_isect_b(self):
        point = Vector3(0.0, 0.0, 55.92)
        e1 = Vector3(55.28, 0.0, 0.0)
        e2 = Vector3(0.0, 54.88, 0.0)
        normal = Vector3(0.0, 0.0, -1.0)
        rectangle = Rectangle(point, e1, e2, normal)

        origin = Vector3(3.0, 2.5, 0.0)
        direction = Vector3(0.0, 0.1, 0.88)
        direction.normalize()
        ray = Ray(origin, direction)

        runtime = Runtime()
        rectangle.isect_asm_b([runtime], "ray_rectangle_intersection")

        assembler = create_assembler()
        mc = assembler.assemble(self.asm_code_bool())
        ds = runtime.load("test", mc)

        Ray.populate_ds(ds, ray, 'ray1')
        Rectangle.populate_ds(ds, rectangle, 'rec1')

        runtime.run("test")
        hp = rectangle.isect(ray)

        if hp is False: self.assertFalse(ds["ret"]!=0)
        if ds["ret"] == 0: self.assertFalse(hp)

if __name__ == "__main__":
    unittest.main()


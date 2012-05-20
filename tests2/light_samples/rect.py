import unittest
from random import random
from tdasm import Runtime
import renmas2

class RectangleIsectTest(unittest.TestCase):
    def setUp(self):
        pass
    
    def asm_code1(self, ren):
        code = """
        #DATA
        """
        code += ren.structures.structs(("hitpoint",)) + """
        hitpoint hp
        #CODE
        mov eax, hp
        call light_rect
        #END
        """
        return code

    def test_light_sample(self):
        runtime = Runtime()
        ren = renmas2.Renderer()
        factory = renmas2.Factory()
        rectangle = factory.create_rectangle(point=(0,0,55.92), e1=(55.28,0,0), e2=(0,54.88,0.0), normal=(0.0,0.0,-1.0))

        ren.macro_call.set_runtimes([runtime])
        mc = rectangle.light_sample_asm('light_rect', ren.assembler, ren.structures)
        ds_rect = runtime.load('light_sample_name', mc)
        rectangle.populate_ds(ds_rect)

        mc = ren.assembler.assemble(self.asm_code1(ren))
        ds = runtime.load("test", mc) 

        runtime.run("test")

        print(ds['hp.light_sample'])
        print(ds['hp.light_normal'])
        print(ds['hp.light_pdf'])

        normal = factory.vector(2.9, 1.2, 4.5)
        normal.normalize()
        hit_point = factory.vector(2.2, 3.3, 4.4)
        hp = renmas2.shapes.HitPoint(1.0, hit_point, normal, 0)
        rectangle.light_sample(hp)
        print(hp.light_sample)
        print(hp.light_normal)
        print(hp.light_pdf)
        

if __name__ == "__main__":
    unittest.main()


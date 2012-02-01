
import unittest
from random import random
from tdasm import Runtime
import renmas2

class SamplingTest(unittest.TestCase):
    def setUp(self):
        pass

    def asm_code1(self, ren):
        code = """
        #DATA
        """
        code += ren.structures.structs(("hitpoint",)) + """
        uint32 next_dir_ptr
        hitpoint hp
        #CODE
        ; call next direction of material
        mov eax, hp
        call dword [next_dir_ptr]
        #END
        """
        return code

    def test_hemisphere_cos(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()

        mat1 = ren.shader.material("default")
        sam = renmas2.materials.HemisphereCos(1.5)
        mat1.add(sam)

        normal = factory.vector(2, 4, 5) 
        normal.normalize()
        hit_point = factory.vector(3, 5, 6)
        hp = renmas2.shapes.HitPoint(1.5, hit_point, normal, 0)

        ren.macro_call.set_runtimes([runtime])
        mat1.next_direction_asm([runtime], ren.structures, ren.assembler)
        mc = ren.assembler.assemble(self.asm_code1(ren))
        ds = runtime.load("test", mc)
        ds["next_dir_ptr"] = runtime.address_module(mat1.nd_asm_name)
        ds["hp.normal"] = (normal.x, normal.y, normal.z, 0.0)
        ds["hp.t"] = 1.5
        ds["hp.hit"] = (hit_point.x, hit_point.y, hit_point.z)
        runtime.run("test")

        print(ds['hp.wi'])
        print(ds['hp.ndotwi'])
        print(ds['hp.pdf'])
        
        mat1.next_direction(hp)
        print(hp.ndotwi)
        print(hp.wi)
        print(hp.pdf)


if __name__ == "__main__":
    unittest.main()


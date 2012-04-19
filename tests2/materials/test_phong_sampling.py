
import unittest
from random import random
from tdasm import Runtime
import renmas2

class PhongSamplingTest(unittest.TestCase):
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

        spec = ren.converter.create_spectrum((0.2, 0.3, 0.1))
        mat1 = renmas2.core.material.Material(ren.converter.zero_spectrum())
        phong = factory.create_phong(spec, 2.0) 
        lam_sampling = renmas2.materials.PhongSampling(2)
        mat1.add(phong)
        mat1.add(lam_sampling)

        normal = factory.vector(2, 4, 5) 
        normal.normalize()
        hit_point = factory.vector(3, 5, 6)
        hp = renmas2.shapes.HitPoint(1.5, hit_point, normal, 0)
        wo = factory.vector(2,5,7)
        wo.normalize()
        hp.wo = wo

        ren.macro_call.set_runtimes([runtime])
        mat1.next_direction_asm([runtime], ren.structures, ren.assembler)
        mc = ren.assembler.assemble(self.asm_code1(ren))
        ds = runtime.load("test", mc)
        ds["next_dir_ptr"] = runtime.address_module(mat1.nd_asm_name)
        ds["hp.normal"] = (normal.x, normal.y, normal.z, 0.0)
        ds["hp.t"] = 1.5
        ds["hp.hit"] = (hit_point.x, hit_point.y, hit_point.z)
        ds["hp.wo"] = (wo.x, wo.y, wo.z, 0.0)
        runtime.run("test")

        mat1.next_direction(hp)
        print("ASM")
        print(ds['hp.wi'])
        print(ds['hp.ndotwi'])
        print(ds['hp.pdf'])
        print("------------") 
        print("Python")
        print(hp.wi)
        print(hp.ndotwi)
        print(hp.pdf)


if __name__ == "__main__":
    unittest.main()



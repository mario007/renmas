
import unittest
from random import random
from tdasm import Runtime
import renmas2

class PefectSampling(unittest.TestCase):
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

    def test_perfect_sampling(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()

        mat = renmas2.core.material.Material(ren.converter.zero_spectrum())
        sam = renmas2.materials.PerfectSpecularSampling()
        mat.add(sam)

        normal = factory.vector(2, 4.5, 5) 
        normal.normalize()
        hit_point = factory.vector(3, 5, 6)
        wo = factory.vector(-2, 1, 0)
        wo.normalize()
        hp = renmas2.shapes.HitPoint(1.5, hit_point, normal, 0)
        hp.wo = wo

        ren.macro_call.set_runtimes([runtime])
        mat.next_direction_asm([runtime], ren.structures, ren.assembler)
        mc = ren.assembler.assemble(self.asm_code1(ren))
        ds = runtime.load("test", mc)
        ds["next_dir_ptr"] = runtime.address_module(mat.nd_asm_name)
        ds["hp.normal"] = (normal.x, normal.y, normal.z, 0.0)
        ds["hp.t"] = 1.5
        ds["hp.hit"] = (hit_point.x, hit_point.y, hit_point.z, 0.0)
        ds["hp.wo"] = (wo.x, wo.y, wo.z, 0.0)
        runtime.run("test")

        print ("PDF =", hp.pdf)
        print ("wi =", hp.wi)
        print ("ndotwi =", hp.ndotwi)
        mat.next_direction(hp)
        print ("PDF =", hp.pdf, " ASM pdf = ", ds["hp.pdf"])
        print ("wi =", hp.wi)
        print ("asm wi", ds["hp.wi"])
        print ("ndotwi =", hp.ndotwi, " asm ndtowi=", ds["hp.ndotwi"])
        print ("normal=", hp.normal)

if __name__ == "__main__":
    unittest.main()


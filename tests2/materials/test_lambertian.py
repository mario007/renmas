
import unittest
from random import random
from tdasm import Runtime
import renmas2

class LambertianTest(unittest.TestCase):
    def setUp(self):
        pass

    def asm_code1(self, ren):
        code = """
        #DATA
        """
        code += ren.structures.structs(("hitpoint",)) + """
        uint32 brdf_ptr
        hitpoint hp
        #CODE
        ; call brdf of material
        mov eax, hp
        call dword [brdf_ptr]
        #END
        """
        return code

    def test_lamb1(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()
        mat = renmas2.core.material.Material(ren.converter.zero_spectrum())

        #mat.f_asm([runtime], ren.assembler, ren.structures)

        mat1 = ren.shader.material("default")
        mat1.f_asm([runtime], ren.assembler, ren.structures)

        mc = ren.assembler.assemble(self.asm_code1(ren))
        ds = runtime.load("test", mc)
        ds["brdf_ptr"] = runtime.address_module(mat1.asm_name)
        runtime.run("test")
        print(ds["hp.f_spectrum.values"])



if __name__ == "__main__":
    unittest.main()


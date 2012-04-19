
import unittest
from random import random
from tdasm import Runtime
import renmas2

class OrenTest(unittest.TestCase):
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

    def populate_ds(self, ds, hp):
        ds["hp.t"] = hp.t
        wi = hp.wi
        ds["hp.wi"] = (wi.x, wi.y, wi.z, 0.0)
        wo = hp.wo
        ds["hp.wo"] = (wo.x, wo.y, wo.z, 0.0)
        ds["hp.ndotwi"] = hp.ndotwi
        n = hp.normal
        ds["hp.normal"] = (n.x, n.y, n.z, 0.0)

    def test_oren1(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()
        mat = renmas2.core.material.Material(ren.converter.zero_spectrum())
        spec = ren.converter.create_spectrum((0.1, 0.3, 0.1))
        ren.macro_call.set_runtimes([runtime])

        oren = factory.create_oren_nayar(spec, 0.45) 
        mat.add(oren)

        t = 2.3
        hit_point = factory.vector(2.2, 3.3, 4.4)
        normal = factory.vector(2.9, 1.2, 4.5)
        normal.normalize()
        ray = factory.create_ray(origin=(4,4,4), direction=(6,7,8))

        hp = renmas2.shapes.HitPoint(t, hit_point, normal, 0, ray)
        wi = factory.vector(-6,10,-3.8)
        wi.normalize()
        hp.wo = ray.dir * -1.0
        hp.wi = wi
        hp.ndotwi = normal.dot(wi)

        mat.f_asm([runtime], ren.assembler, ren.structures)
        mc = ren.assembler.assemble(self.asm_code1(ren))
        ds = runtime.load("test", mc)
        self.populate_ds(ds, hp)
        ds["brdf_ptr"] = runtime.address_module(mat.f_asm_name)
        runtime.run("test")

        spectrum = mat.f(hp)
        print(spectrum)
        print(ds["hp.f_spectrum.values"])

if __name__ == "__main__":
    unittest.main()


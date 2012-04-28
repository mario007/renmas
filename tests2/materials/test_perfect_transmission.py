
import unittest
from random import random
from tdasm import Runtime
import renmas2

class PerfectTransmissionTest(unittest.TestCase):
    def setUp(self):
        pass

    def asm_code1(self, ren):
        code = """
        #DATA
        """
        code += ren.structures.structs(("hitpoint",)) + """
        uint32 btdf_ptr
        hitpoint hp
        #CODE
        ; call btdf of material
        mov eax, hp
        call dword [btdf_ptr]
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
        if hp.fliped:
            ds["hp.fliped"] = 1
        else:
            ds["hp.fliped"] = 0
        ds["hp.specular"] = 65 


    def test_perfect_specular(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()
        mat = renmas2.core.material.Material(ren.converter.zero_spectrum())
        spec = ren.converter.create_spectrum((0.5, 0.5, 0.5))
        ren.macro_call.set_runtimes([runtime])

        eta_in = ren.converter.zero_spectrum().set(1.3)
        eta_out = ren.converter.zero_spectrum().set(1.0)
        fresnel = renmas2.materials.FresnelDielectric(eta_in, eta_out) 

        perf_spec = renmas2.materials.PerfectTransmission(spec, fresnel, 1.0)
        mat.add(perf_spec)

        t = 2.3
        hit_point = factory.vector(2.2, 3.1, 4.4)
        normal = factory.vector(2.9, 1.2, 4.5)
        normal.normalize()
        hp = renmas2.shapes.HitPoint(t, hit_point, normal, 0)
        wi = factory.vector(6,-8,3.8)
        #wi = wi * -1.0
        wi.normalize()
        wo = factory.vector(2, 2, 4)
        wo.normalize()
        hp.wo = wo
        hp.wi = wi
        hp.ndotwi = normal.dot(wi)
        hp.fliped = True 
        hp.specular = 65 

        mat.btdf_asm([runtime], ren.assembler, ren.structures)
        mc = ren.assembler.assemble(self.asm_code1(ren))
        ds = runtime.load("test", mc)
        self.populate_ds(ds, hp)
        ds["btdf_ptr"] = runtime.address_module(mat.btdf_asm_name)
        runtime.run("test")

        spectrum = mat.btdf(hp)
        print("Python")
        print(spectrum)
        print("---------------------------------------")
        print("Asm")
        print(ds["hp.f_spectrum.values"])


if __name__ == "__main__":
    unittest.main()




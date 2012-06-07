
import unittest
from random import random
from tdasm import Runtime
import renmas2

class PerfectSpecularTest(unittest.TestCase):
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
        if hp.fliped:
            ds["hp.fliped"] = 1
        else:
            ds["hp.fliped"] = 0
        ds["hp.specular"] = 89

    def shlick(self, n, cosi):
        r0 = (n-1.0)/(n+1.0)
        r0 = r0 * r0
        return r0 + (1-r0)*pow(1-cosi, 5.0)

    def test_perfect_specular(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()
        mat = renmas2.core.material.Material(ren.converter.zero_spectrum())
        spec = ren.converter.create_spectrum((1.0, 1.0, 1.0))
        ren.macro_call.set_runtimes([runtime])

        eta_in = ren.converter.zero_spectrum().set(1.5)
        eta_out = ren.converter.zero_spectrum().set(1.0)
        fresnel = renmas2.materials.FresnelDielectric(eta_in, eta_out) 

        perf_spec = renmas2.materials.PerfectSpecular(spec, fresnel, 1.0)
        mat.add(perf_spec)

        t = 2.3
        hit_point = factory.vector(2.2, 3.1, 4.4)
        normal = factory.vector(2.9, 1.2, 4.5)
        normal.normalize()
        hp = renmas2.shapes.HitPoint(t, hit_point, normal, 0)
        wi = factory.vector(6,-27,3.8)
        wi.normalize()
        wo = factory.vector(2, 2, 4)
        wo.normalize()
        hp.wo = wo
        hp.wi = wi
        hp.ndotwi = normal.dot(wi)
        print (hp.ndotwi)
        hp.fliped = True 
        hp.specular = 89

        mat.f_asm([runtime], ren.assembler, ren.structures)
        mc = ren.assembler.assemble(self.asm_code1(ren))
        ds = runtime.load("test", mc)
        self.populate_ds(ds, hp)
        ds["brdf_ptr"] = runtime.address_module(mat.f_asm_name)
        runtime.run("test")

        spectrum = mat.f(hp)
        print("shlick", self.shlick(1.5, hp.ndotwi))
        print("Python")
        print(spectrum)
        print("---------------------------------------")
        print("Asm")
        print(ds["hp.f_spectrum.values"])


if __name__ == "__main__":
    unittest.main()



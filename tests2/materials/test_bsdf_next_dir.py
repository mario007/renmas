
import unittest
from random import random
from tdasm import Runtime
import renmas2

class TransmissionSampling(unittest.TestCase):
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

    def test_transmission_sampling(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()

        mat = renmas2.core.material.Material(ren.converter.zero_spectrum())
        eta_in = 1.3
        eta_out = 1.0
        sampling = renmas2.materials.PerfectTransmissionSampling(eta_in, eta_out)
        mat.add(sampling)

        eta_in = ren.converter.zero_spectrum().set(1.3)
        eta_out = ren.converter.zero_spectrum().set(1.0)
        fresnel = renmas2.materials.FresnelDielectric(eta_in, eta_out) 
        spec = ren.converter.create_spectrum((0.5, 0.5, 0.5))

        perf_spec = renmas2.materials.PerfectTransmission(spec, fresnel, 1.0)
        mat.add(perf_spec)

        ref_sam = renmas2.materials.PerfectSpecularSampling()
        mat.add(ref_sam)

        spec2 = ren.converter.create_spectrum((0.9, 0.9, 0.9))
        fresnel2 = renmas2.materials.FresnelDielectric(eta_in, eta_out) 
        perf_ref = renmas2.materials.PerfectSpecular(spec2, fresnel2, 1.0)
        mat.add(perf_ref)

        normal = factory.vector(2, 4.5, 5) 
        normal.normalize()
        hit_point = factory.vector(3, 5, 6)
        wo = factory.vector(-2, 1, 0)
        wo.normalize()
        hp = renmas2.shapes.HitPoint(1.5, hit_point, normal, 0)
        hp.wo = wo
        hp.fliped = False 

        ren.macro_call.set_runtimes([runtime])
        mat.next_direction_bsdf_asm([runtime], ren.structures, ren.assembler)
        mc = ren.assembler.assemble(self.asm_code1(ren))
        ds = runtime.load("test", mc)

        ds["next_dir_ptr"] = runtime.address_module(mat.nd_asm_name)
        ds["hp.normal"] = (normal.x, normal.y, normal.z, 0.0)
        ds["hp.t"] = 1.5
        ds["hp.hit"] = (hit_point.x, hit_point.y, hit_point.z, 0.0)
        ds["hp.wo"] = (wo.x, wo.y, wo.z, 0.0)
        ds["hp.fliped"] = 0
        runtime.run("test")

        mat.next_direction_bsdf(hp)
        print ("Python")
        print (hp.wi)
        print (hp.ndotwi)
        print (hp.specular)
        print (hp.f_spectrum)
        print ("ASM")
        print (ds["hp.wi"])
        print (ds["hp.ndotwi"])
        print (ds["hp.specular"])
        print (ds["hp.f_spectrum.values"])


if __name__ == "__main__":
    unittest.main()


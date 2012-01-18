
import unittest
from random import random
from tdasm import Runtime
import renmas2

class ShaderTest(unittest.TestCase):
    def setUp(self):
        pass

    def asm_code1(self, ren):
        code = """
        #DATA
        """
        code += ren.structures.structs(("hitpoint",)) + """
        hitpoint hp
        float p1[4]
        float p2[4]
        #CODE
        macro eq128 xmm0 = p1
        macro eq128 xmm1 = p2
        call ray_scene_visibility
        mov eax, hp
        call shade
        #END
        """
        return code

    def asm_code2(self, ren):
        code = """
        #DATA
        """
        code += ren.structures.structs(("hitpoint",)) + """
        hitpoint hp
        float p1[4]
        float p2[4]
        #CODE
        macro eq128 xmm0 = p1
        macro eq128 xmm1 = p2
        call ray_scene_visibility
        #END
        """
        return code

    def test_shader1(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        irender = renmas2.IRender(ren)
        #ren.spectral_rendering = True
        runtime = Runtime()
        irender.add_light(type="pointlight", name="light1", source=(4.0,4.0,4.0), position=(10.1,10,10))
        irender.add_shape(type="sphere", name="Sphere00", radius=3.0, position=(0.0, 0.0, 0.0))
        ren.prepare()

        ren.intersector.visibility_asm([runtime], "ray_scene_visibility")
        ren.shader.shade_asm([runtime], "shade", "ray_scene_visibility")
        mc = ren.assembler.assemble(self.asm_code1(ren))
        ds = runtime.load("test", mc)
        ds["hp.hit"] = (4.4, 2.2, 1.0, 0.0)
        ds["hp.t"] = 2.2 
        ds["hp.normal"] = (0.0, 1.0, 0.0, 0.0)
        ds["hp.mat_index"] = 0

        runtime.run("test")
        hit = renmas2.Vector3(4.4, 2.2, 1.0)
        normal = renmas2.Vector3(0.0, 1.0, 0.0)
        hp = renmas2.shapes.HitPoint(2.2, hit, normal, 0)
        ret = ren.shader.shade(hp)
        print(ret)
        print (ds["hp.l_spectrum.values"])

if __name__ == "__main__":
    unittest.main()


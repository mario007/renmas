
import unittest
from tdasm import Runtime
import renmas2

class SkySpectrumTest(unittest.TestCase):
    def setUp(self):
        pass

    def asm_code1(self, ren):
        code = """
        #DATA
        """
        code += ren.structures.structs(('spectrum',)) + """
        spectrum spec
        float dir[4]
        
        float temp[4]
        #CODE

        mov eax, spec
        macro eq128 xmm0 = dir
        call get_sky_spectrum 

        macro eq128 temp = xmm0 {xmm7}

        #END
        """
        return code

    def test_getsky(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()
        ren.spectral_rendering = True 

        ren.macro_call.set_runtimes([runtime])
        sk = renmas2.lights.SunSky(renderer=ren, latitude=80.0, longitude=43.0, sm=0, jd=224, time_of_day=16.50, turbidity=3.0)

        direction = renmas2.Vector3(3.2, 0.01, 1.8)
        direction.normalize()
        
        sk.get_sky_spectrum_asm('get_sky_spectrum', [runtime])
        mc = ren.assembler.assemble(self.asm_code1(ren))
        ds = runtime.load("test", mc)
        ds['dir'] = (direction.x, direction.y, direction.z, 0.0) 
        ds['spec.values'] = ren.converter.zero_spectrum().set(1.0).to_ds()

        runtime.run('test')
        spec = sk.get_sky_spectrum(direction)
        
        print(spec)
        print(ds['spec.values'])

if __name__ == "__main__":
    unittest.main()


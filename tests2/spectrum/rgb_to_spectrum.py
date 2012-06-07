import unittest
from tdasm import Runtime
import renmas2

class RGBToSpectrumTest(unittest.TestCase):
    def setUp(self):
        pass

    def asm_code1(self, ren):
        code = """
        #DATA
        """
        code += ren.structures.structs(('spectrum',)) + """
        float rgb[4]
        spectrum spec

        #CODE

        macro eq128 xmm0 = rgb 
        mov eax, spec

        call rgb_to_spectrum

        #END
        """
        return code

    def test_conversion(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()

        ren.spectral_rendering = True
        conv = ren.converter
        conv.rgb_to_spectrum_asm("rgb_to_spectrum", [runtime])

        mc = ren.assembler.assemble(self.asm_code1(ren))
        ds = runtime.load("test", mc)

        ds['rgb'] = (0.53, 0.46, 0.15, 0.0) 

        runtime.run('test')
        print("Konverzija")
        spec = conv.rgb_to_sampled((0.53, 0.46, 0.15))

        print(spec)
        print(ds['spec.values'])


if __name__ == "__main__":
    unittest.main()



import unittest
from tdasm import Runtime
import renmas2

class ChromacityTest(unittest.TestCase):
    def setUp(self):
        pass

    def asm_code1(self, ren):
        code = """
        #DATA
        """
        code += ren.structures.structs(('spectrum',)) + """
        float x, y
        spectrum spec

        #CODE

        macro eq32 xmm0 = x
        macro eq32 xmm1 = y
        mov eax, spec

        call chromacity_to_spectrum

        #END
        """
        return code

    def test_conversion(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()

        ren.spectral_rendering = True
        conv = ren.converter
        conv.chromacity_to_spectrum_asm("chromacity_to_spectrum", [runtime])
        spec = conv.chromacity_to_spectrum(0.35, 0.25)
        print(spec)

        mc = ren.assembler.assemble(self.asm_code1(ren))
        ds = runtime.load("test", mc)
        ds['x'] = 0.35
        ds['y'] = 0.25

        runtime.run('test')
        print(ds['spec.values'])


if __name__ == "__main__":
    unittest.main()


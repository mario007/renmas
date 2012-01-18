
import unittest
from random import random
from tdasm import Runtime
import renmas2
import renmas2.samplers

class FilmTest(unittest.TestCase):
    def setUp(self):
        pass

    def asm_code(self, ren):
        code = """
            #DATA
        """
        code += ren.structures.structs(('sample', 'spectrum')) + """
            sample sp1 
            spectrum spec1

            #CODE
            mov eax, spec1
            mov ebx, sp1
            call add_sample

            #END
        """
        return code

    def test_addsample(self):
        ren = renmas2.Renderer()
        runtime = Runtime()

        #ren.spectrum_rendering = True
        ren.film.nsamples = 2 
        ren.prepare()
        ren.converter.to_rgb_asm("spectrum_to_rgb", [runtime])
        ren.film.add_sample_asm([runtime], "add_sample", "spectrum_to_rgb")
        mc = ren.assembler.assemble(self.asm_code(ren))
        ds = runtime.load("test", mc)

        ds["sp1.ix"] = 10
        ds["sp1.iy"] = 10
        ds["sp1.xyxy"] = (10.4, 10.4, 10.4, 10.4)
        sample = renmas2.samplers.Sample(10.4, 10.4, 10, 10, 0.5)
        spec = ren.converter.create_spectrum((0.70, 0.2, 0.3))
        ren.film.add_sample(sample, spec)
        ds["spec1.values"] = spec.to_ds()
        runtime.run("test")

        ds["sp1.ix"] = 15
        ds["sp1.iy"] = 19
        ds["sp1.xyxy"] = (15.7, 19.4, 15.7, 19.4)
        sample = renmas2.samplers.Sample(10.4, 10.4, 15, 19, 0.5)
        spec = ren.converter.create_spectrum((0.50, 0.4, 0.1))
        ren.film.add_sample(sample, spec)
        ds["spec1.values"] = spec.to_ds()
        runtime.run("test")

        print(ren.film._ds[0]["temp"])


if __name__ == "__main__":
    unittest.main()


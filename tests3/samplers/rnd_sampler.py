import unittest

from tdasm import Runtime

from renmas3.samplers import RandomSampler
from renmas3.core import ColorManager, Tile
from renmas3.core.structures import SAMPLE

class RegularSamplerTest(unittest.TestCase):
    def setUp(self):
        pass

    def asm_code(self):
        ASM_CODE = " #DATA \n" + SAMPLE + """
            sample sample1
            uint32 kraj 
            #CODE
            macro mov eax, sample1
            call get_sample
            mov dword [kraj], eax
            #END
        """
        return ASM_CODE
    
    def show_samples(self, sample, ds):
        x1, y1 = sample.x, sample.y
        x2, y2, tmp1, tmp2 = ds['sample1.xyxy']
        
        print('****************************')
        print(x1, x2)
        print(y1, y2)

        ix1, iy1 = sample.ix, sample.iy
        ix2, iy2 = ds['sample1.ix'], ds['sample1.iy']
        self.assertEqual(ix1, ix2)
        self.assertEqual(iy1, iy2)

    def test1(self):
        mgr = ColorManager()
        
        sampler = RandomSampler(2, 2, pixel=1.0)
        tile = Tile(0, 0, 3, 3)
        tile.split(1)
        runtime = Runtime()
        mgr.macro_call.set_runtimes([runtime])

        sampler.get_sample_asm([runtime], "get_sample", mgr.assembler)
        mc = mgr.assembler.assemble(self.asm_code())
        ds = runtime.load('test', mc)

        sampler.set_tile(tile)

        while True:
            sample = sampler.get_sample()
            if sample is None:
                break

            runtime.run('test')
            self.show_samples(sample, ds)
        
        runtime.run('test')
        ret = ds['kraj']
        self.assertFalse(ret)

if __name__ == "__main__":
    unittest.main()


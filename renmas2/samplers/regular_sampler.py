
import renmas2
import renmas2.core
from ..core import get_structs
from ..macros import macro_call, assembler
from .sample import Sample
from .sampler import Sampler

# xw = s(x - width/2 + 0.5)
# yw = s(y - height/2 + 0.5)
class RegularSampler(Sampler):
    def __init__(self, width, height, pixel=1.0):
        super(RegularSampler, self).__init__(width, height, 1, pixel)
        self._ds = None

    def _update_ds(self):
        if self._ds is None: return
        for x in range(len(self._tile.lst_tiles)):
            ds = self._ds[x]
            tile = self._tile.lst_tiles[x]
            ds["endx"] = tile.x + tile.width 
            ds["endy"] = tile.y + tile.height 
            ds["tilex"] = tile.x 
            ds["tiley"] = tile.y
            curx = tile.x - 1
            cury = tile.y
            ds["cur_xyxy"] = (curx, cury, curx, cury)
            ds["pixel_size"] = (self._pixel_size, self._pixel_size, self._pixel_size, self._pixel_size)
            w2 = -float(self._width) * 0.5 + 0.5   
            h2 = -float(self._height) * 0.5  + 0.5
            ds["w2h2"] = (w2, h2, w2, h2)


    # xw = s(x - width/2 + 0.5)
    # yw = s(y - height/2 + 0.5)
    def get_sample(self):

        self._curx += 1
        if self._curx == self._endx:
            self._curx = self._tile.x
            self._cury += 1
            if self._cury == self._endy:
                return None
        
        x = self._pixel_size * (self._curx + self._w2)  
        y = self._pixel_size * (self._cury + self._h2)
        return Sample(x, y, self._curx, self._cury, 1.0)

    # eax - pointer to sample structure
    def get_sample_asm(self, runtimes, label):

        code = """
            #DATA
        """
        code += get_structs(('sample',)) + """
            uint32 endx, endy
            uint32 tilex, tiley
            uint32 cur_xyxy[4] ; we just use first two numbers
            float pixel_size[4]
            float w2h2[4]
            #CODE
        """
        code += " global " + label + ":\n" + """
            add dword [cur_xyxy], 1
            mov ebx, dword [cur_xyxy] 
            cmp ebx, dword [endx]
            jne _gen_sam
            mov ecx, dword [tilex]
            mov dword [cur_xyxy], ecx
            add dword [cur_xyxy + 4], 1
            mov edx, dword [cur_xyxy + 4]
            cmp edx, dword [endy]
            jne _gen_sam
            mov eax, 0 ;end of sampling
            ret

            _gen_sam:
            macro eq128 xmm0 = cur_xyxy
            macro call int_to_float xmm1, xmm0
            macro eq128 xmm1 = xmm1 + w2h2
            macro eq128 xmm1 = xmm1 * pixel_size
            macro eq128 eax.sample.xyxy = xmm1 {xmm0}
           
            mov ebx, dword [cur_xyxy] 
            mov ecx, dword [cur_xyxy + 4]
            mov dword [eax + sample.ix] ,ebx
            mov dword [eax + sample.iy] ,ecx
            mov eax, 1
            ret
            
        """
        macro_call.set_runtimes(runtimes)
        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "get_sample" + str(hash(self))
        self._ds = []
        for r in runtimes:
            self._ds.append(r.load(name, mc))


    def set_tile(self, tile):
        super(RegularSampler, self).set_tile(tile)
        self._curx = tile.x - 1
        self._endx = tile.x + tile.width
        self._endy = tile.y + tile.height
        self._w2 = -float(self._width) * 0.5  + 0.5 
        self._h2 = -float(self._height) * 0.5 + 0.5 
        
    def spp(self, dummy):
        pass


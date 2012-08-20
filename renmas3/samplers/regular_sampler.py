import platform

from .sample import Sample
from .sampler import Sampler

# xw = s(x - width/2 + 0.5)
# yw = s(y - height/2 + 0.5)
class RegularSampler(Sampler):
    def __init__(self, width, height, pixel=1.0):
        super(RegularSampler, self).__init__(width, height, 1, pixel)
        self._ds = None

    def _update_ds(self, tile):
        if self._ds is None:
            return
        for ds, tile in zip(self._ds, tile.lst_tiles):
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
    def get_sample_asm(self, runtimes, label, assembler):
        bits = platform.architecture()[0]
        code = """
            #DATA
        """
        code += Sample.struct() + """
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
        """
        if bits == '64bit':
            code += """
            mov dword [rax + sample.ix] ,ebx
            mov dword [rax + sample.iy] ,ecx
            """
        else:
            code += """
            mov dword [eax + sample.ix] ,ebx
            mov dword [eax + sample.iy] ,ecx
            """
        code += """
            mov eax, 1
            ret
            
        """
        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "get_sample" + str(hash(self))
        self._ds = []
        for r in runtimes:
            self._ds.append(r.load(name, mc))

    def set_tile(self, tile):
        self._tile = tile
        self._curx = tile.x - 1
        self._cury = tile.y
        self._endx = tile.x + tile.width
        self._endy = tile.y + tile.height
        self._w2 = -float(self._width) * 0.5  + 0.5 
        self._h2 = -float(self._height) * 0.5 + 0.5 
        self._update_ds(tile)
        
    def set_spp(self, dummy):
        self._spp = 1


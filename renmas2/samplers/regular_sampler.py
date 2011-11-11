
import renmas2
import renmas2.core
from ..core import Sampler
from tdasm import Tdasm, Runtime
import x86

# xw = s(x - width/2 + 0.5)
# yw = s(y - height/2 + 0.5)
class RegularSampler(Sampler):
    def __init__(self, width, height, pixel=1.0):
        super(RegularSampler, self).__init__(width, height, 1, pixel)

    def _generate_samples_python(self, tile):
        darr = self._sample_array
        xyxy_off = darr.member_offset('xyxy')
        ix_off = darr.member_offset('ix')
        iy_off = darr.member_offset('iy')
        ray_origin = darr.member_offset('cam_ray.origin')
        ray_dir = darr.member_offset('cam_ray.dir')
        darr_adr = darr.get_addr()
        sample_size = darr.obj_size()

        req_samples = tile.width * tile.height * self.n
        w2 = -float(self.width) / 2.0  
        h2 = -float(self.height) / 2.0  
        curx = tile.x - 1
        cury = tile.y
        tile_endx = tile.x + tile.width
        tile_endy = tile.y + tile.height

        for idx in range(req_samples):
            curx += 1
            if curx == tile_endx: 
                curx = tile.x 
                cury += 1
            if cury == tile_endy: 
                self.end_sampling = True
                break

            x = self.pixel_size * (curx + w2 + 0.5)  
            y = self.pixel_size * (cury + h2 + 0.5)
            ix = curx
            iy = cury
            adr = darr_adr + idx*sample_size
            x86.SetFloat(adr + xyxy_off, (x,y,x,y), 0)
            x86.SetUInt32(adr + ix_off, ix, 0)
            x86.SetUInt32(adr + iy_off, iy, 0)
            if self.camera:
                self.camera.generate_ray(adr+xyxy_off, adr+ray_origin, adr+ray_dir)
                
        return req_samples

    def _get_assembly_code(self):
        asm_structs = self.structures.get_struct("ray")
        asm_structs += self.structures.get_struct("sample")

        code = """
            #DATA
        """
        code += asm_structs + """
            float pxpy[4] = 0.5, 0.5, 0.5, 0.5 
            int32 tile_endx, tile_endy
            int32 tilex, tiley
            int32 cur_xyxy[4] ; we just use first two numbers for now
            float pixel_size[4]
            float w2h2[4]

            uint32 adr_arr

            #CODE
            mov esi, dword [adr_arr]
            main_loop:
            macro eq128 xmm6 = w2h2
            macro eq128 xmm7 = xmm6 + pxpy
            macro eq128 xmm5 = pixel_size

            add dword [cur_xyxy], 1 ;increment x
            mov eax, dword [cur_xyxy]
            cmp eax, dword [tile_endx]
            jne _next
            mov ebx, dword [tilex]
            add dword [cur_xyxy + 4], 1 ;increment y
            mov dword [cur_xyxy], ebx
            _next:
            mov eax, dword [cur_xyxy + 4] 
            cmp eax, dword [tile_endy]
            jne _next2
            jmp _end_sampling
            _next2:

            macro eq128 xmm0 = cur_xyxy
            macro call int_to_float xmm0, xmm0
            macro eq128 xmm0 = xmm0 + xmm7
            macro eq128 xmm0 = xmm0 * xmm5

            mov eax, dword [cur_xyxy]
            mov ebx, dword [cur_xyxy + 4]

            mov dword [esi + sample.ix], eax 
            mov dword [esi + sample.iy], ebx
            macro eq128 esi.sample.xyxy = xmm0 {xmm0}
        """
        if self.camera:
            code += """
                    push esi
                    mov eax, esi
                    call generate_ray
                    pop esi
            """

        code += """
            mov edx, sizeof sample
            add esi, edx
            jmp main_loop

            _end_sampling:
            #END
            
        """
        return code

    def _populate_data(self, ds, tile, addr=None):
        if ds is None: return
        ds["tile_endx"] = tile.x + tile.width 
        ds["tile_endy"] = tile.y + tile.height 
        ds["tilex"] = tile.x 
        ds["tiley"] = tile.y
        curx = tile.x - 1
        cury = tile.y
        ds["cur_xyxy"] = (curx, cury, curx, cury)
        ds["pixel_size"] = (self.pixel_size, self.pixel_size, self.pixel_size, self.pixel_size)
        w2 = -float(self.width) * 0.5   
        h2 = -float(self.height) * 0.5  
        ds["w2h2"] = (w2, h2, w2, h2)
        if addr:
            ds["adr_arr"] = addr
        else:
            ds["adr_arr"] = self._sample_array.get_addr()


    def nsamples(self):
        return 1 

    def set_samples_per_pixel(self, num):
        pass


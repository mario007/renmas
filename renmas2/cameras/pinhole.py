
import x86
from ..core import Camera 

class Pinhole(Camera):
    def __init__(self, eye, lookat, distance=100):
        super(Pinhole, self).__init__(eye, lookat, distance)

    def _generate_rays_python(self, nsamples, idx, sample_arr):

        xyxy_off = sample_arr.member_offset('xyxy')
        address = sample_arr.get_addr()
        sample_size = sample_arr.obj_size()

        address = address + sample_size * idx
        dist =  self.w * self.distance

        dir_offset = self._ray_array.member_offset('dir')
        eye_offset = self._ray_array.member_offset('origin')
        ray_adr = self._ray_array.get_addr()
        ray_size = self._ray_array.obj_size()
        
        ex, ey, ez = self.eye.x, self.eye.y, self.eye.z

        for n in range(nsamples):
            x, y = x86.GetFloat(address + xyxy_off, 0, 2)
            d = self.u * x + self.v * y - dist
            d.normalize()

            x86.SetFloat(ray_adr + dir_offset, (d.x, d.y, d.z, 0.0), 0)
            x86.SetFloat(ray_adr + eye_offset, (ex, ey, ez, 0.0), 0)

            address += sample_size
            ray_adr += ray_size

    def _get_assembly_code(self):
        asm_structs = self.structures.get_struct('sample')
        asm_structs += self.structures.get_struct('ray')

        code = """
            #DATA
        """
        code += asm_structs + """
            float u[4] 
            float v[4]
            float wdistance[4]
            float eye[4]

            uint32 adr_rays
            uint32 adr_samples
            uint32 nsamples

            float dir[256] 
            uint32 nrays

            #CODE
            mov eax, dword [adr_samples]
            mov ebx, dword [adr_rays]
            mov ecx, dword [nsamples]
            mov esi, sizeof ray
            mov edi, sizeof sample
            mov dword [nrays], 0
            
            main_loop:
            macro eq128 xmm0 = eax.sample.xyxy 
            macro broadcast xmm1 = xmm0[0]
            macro eq128 xmm3 = u * xmm1
            macro broadcast xmm2 = xmm0[1]
            macro eq128 xmm4 = v * xmm2
            macro eq128 xmm5 = xmm3 + xmm4 - wdistance
            macro normalization xmm5 {xmm6, xmm7}
            
            ;macro eq128 ebx.ray.origin = eye {xmm0}
            ;macro eq128 ebx.ray.dir = xmm5 {xmm0}


            add eax, edi
            ;add ebx, esi

            cmp dword [nrays], 64
            je _write_ray

            _nazad:
            sub ecx, 1
            jnz main_loop

            #END

            _write_ray:
            mov edi, dir

            macro eq128 ebx.ray.origin = eye {xmm0} 
            macro eq128 ebx.ray.dir = edi {xmm0}

            add ebx, esi
            add edi, 16
            sub dword [nrays], 1
            jnz _write_ray
            jmp _nazad
            

        """
        return code

    def _populate_data(self, ds):
        if ds is None: return
        u = self.u
        v = self.v
        wd = self.w * self.distance
        eye = self.eye
        ds["u"] = (u.x, u.y, u.z, 0.0) 
        ds["v"] = (v.x, v.y, v.z, 0.0)
        ds["wdistance"] = (wd.x, wd.y, wd.z, 0.0)
        ds["eye"] = (eye.x, eye.y, eye.z, 0.0)


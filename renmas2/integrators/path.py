
import x86
from tdasm import Runtime
from .integrator import Integrator 
from ..core import Spectrum, Ray
from ..shapes import HitPoint
import renmas2.switch as proc

class Pathtracer(Integrator):
    def __init__(self, renderer):
        super(Pathtracer, self).__init__(renderer)
        self._ds = None

    def render_py(self, tile):
        ren = self._renderer
        sampler = ren.sampler
        sampler.set_tile(tile)
        camera = ren.camera
        intersector = ren.intersector
        film = ren.film
        shader = ren.shader
        conv = ren.converter

        background = ren.converter.create_spectrum((0.00, 0.0, 0.0))

        path = background.zero_spectrum()
        path.set(1.0)
        max_depth = 3
        treshold = 0.7 
        counter = 0

        while True:
            sam = sampler.get_sample()
            if sam is None: break 
            ray = camera.ray(sam) 
            hp = intersector.isect(ray) 
            if hp:
                L = background.zero_spectrum()
                path = background.zero_spectrum()
                path.set(1.0)
                cur_depth = 1
                while True:
                    hp.wo = ray.dir * -1.0
                    spectrum = shader.shade(hp)
                    L = L + spectrum.mix_spectrum(path)
                    Y = conv.Y(path)
                    #print(cur_depth, Y)
                    if cur_depth >= max_depth or Y < treshold: break
                    material = shader._materials_idx[hp.material]
                    material.next_direction(hp)
                    material.f(hp)
                    path = path.mix_spectrum(hp.f_spectrum * (abs(hp.ndotwi)/hp.pdf))
                    cur_depth += 1

                    ray = Ray(hp.hit_point, hp.wi)
                    hp = intersector.isect(ray) 
                    if not hp: break
                    
                film.add_sample(sam, L)
            else:
                film.add_sample(sam, background)

    def _algorithm_asm(self, runtimes):
        
        code = """
            #DATA
        """
        mat_list = self._renderer.shader._materials_lst

        if proc.AVX:
            absolute = "vandps xmm0, xmm0, oword [absolute] \n"
        else:
            absolute = "andps xmm0, oword [absolute] \n"

        code += self._renderer.structures.structs(('sample', 'ray', 'hitpoint')) + """
            sample sample1
            ray ray1
            float minus_one[4] = -1.0, -1.0, -1.0, 0.0
            float one[4] = 1.0, 1.0, 1.0, 1.0
            hitpoint hp1
            uint32 max_depth = 8
            uint32 cur_depth = 0
            spectrum path
            spectrum L
            spectrum background
            spectrum temp_spectrum
            float treshold = 0.01
            uint32 absolute[4] = 0x7FFFFFFF, 0x7FFFFFFF, 0x7FFFFFFF, 0x7FFFFFFF
            """
        code += "uint32 materials_ptrs[" + str(len(mat_list)) + "]\n"
        code += "uint32 samplings[" + str(len(mat_list)) + "]\n"
        code += """

            #CODE
            _main_loop:
            mov eax, sample1
            call get_sample
            cmp eax, 0
            je _end_rendering

            mov eax, sample1
            mov ebx, ray1
            call get_ray

            ; eax = pointer_to_ray, ebx = pointer_to_hitpoint
            mov eax, ray1 
            mov ebx, hp1 
            call ray_scene_intersection 

            cmp eax, 0
            je _write_background

            ; set path = 1.0 , L = 0.0
            macro eq128 xmm0 = one
            mov eax, path
            macro spectrum eax = xmm0
            macro call zero xmm0
            mov eax, L
            macro spectrum eax = xmm0
            mov dword [cur_depth], 1

            _inner_loop:
            ; call shading routine
            mov eax, hp1
            mov ebx, ray1 
            macro eq128 eax.hitpoint.wo = ebx.ray.dir * minus_one {xmm0} 
            call shade

            mov ecx, hp1
            lea eax, dword [ecx + hitpoint.l_spectrum]
            mov ebx, path
            mov ecx, temp_spectrum
            macro spectrum ecx = ebx * eax 
            mov eax, L
            macro spectrum eax = eax + ecx 
            mov eax, path
            call lumminance
            macro if xmm0 < treshold goto _write_sample
            mov eax, dword [max_depth]
            cmp eax, dword [cur_depth]
            je _write_sample
            ; call next direction and  brdf of material
            mov eax, hp1 
            mov ebx, dword [eax + hitpoint.mat_index]
            call dword [samplings + 4*ebx] 
            mov eax, hp1
            mov ebx, dword [eax + hitpoint.mat_index]
            call dword [materials_ptrs + 4*ebx] 
            mov eax, hp1
            macro eq32 xmm0 = eax.hitpoint.ndotwi
            """
        code += absolute + """
            ;macro eq128 xmm0 = xmm0 & absolute
            macro eq32 xmm0 = xmm0 / eax.hitpoint.pdf
            ;macro eq32 xmm0 = eax.hitpoint.ndotwi / eax.hitpoint.pdf
            lea ebx, dword [eax + hitpoint.f_spectrum]
            mov ecx, temp_spectrum
            macro spectrum ecx = xmm0 * ebx
            mov eax, path
            macro spectrum eax = eax * ecx
            add dword [cur_depth], 1

            mov eax, ray1
            mov ebx, hp1
            macro eq128 eax.ray.dir = ebx.hitpoint.wi {xmm0}
            macro eq128 eax.ray.origin = ebx.hitpoint.hit {xmm0}

            mov eax, ray1 
            mov ebx, hp1 
            call ray_scene_intersection 
            cmp eax, 0
            jne _inner_loop
            
            
            _write_sample:
            mov eax, L 
            mov ebx, sample1
            call add_sample
            jmp _main_loop

            _write_background:
            mov eax, background 
            mov ebx, sample1 
            call add_sample

            jmp _main_loop

            _end_rendering:
            #END
        """

        ren = self._renderer
        for m in mat_list:
            m.next_direction_asm(runtimes, ren.structures, ren.assembler)

        mc = self._renderer.assembler.assemble(code)
        #mc.print_machine_code()
        name = "pathtracer_integrator"
        self._ds = []
        for r in runtimes:
            ds = r.load(name, mc)
            self._ds.append(ds)
            m_ptrs = [r.address_module(m.f_asm_name) for m in mat_list]
            ds["materials_ptrs"] = tuple(m_ptrs)
            samplings_ptr = [r.address_module(m.nd_asm_name) for m in mat_list]
            ds["samplings"] = tuple(samplings_ptr)

        self._populate_ds()

    def _populate_ds(self):
        if self._ds is None: return
        for ds in self._ds:
            ds['background.values'] = self._background.to_ds()

    def render_asm(self, tile):
        self._renderer.sampler.set_tile(tile)
        runtimes = self._runtimes
        
        addrs = []
        for i in range(len(tile.lst_tiles)):
            r = runtimes[i]
            addrs.append(r.address_module('pathtracer_integrator'))

        x86.ExecuteModules(tuple(addrs))

    def prepare(self):
        ren = self._renderer
        self._background = ren.converter.create_spectrum((0.00, 0.0, 0.0))

        self._runtimes = [Runtime() for n in range(ren.threads)] 
        ren.macro_call.set_runtimes(self._runtimes)
        ren.sampler.get_sample_asm(self._runtimes, 'get_sample', ren.assembler, ren.structures)
        ren.camera.ray_asm(self._runtimes, 'get_ray', ren.assembler, ren.structures)
        ren.intersector.isect_asm(self._runtimes, 'ray_scene_intersection')
        ren.converter.to_rgb_asm("spectrum_to_rgb", self._runtimes)
        ren.film.add_sample_asm(self._runtimes, "add_sample", "spectrum_to_rgb")
        ren.intersector.visibility_asm(self._runtimes, "ray_scene_visibility")
        ren.shader.shade_asm(self._runtimes, "shade", "ray_scene_visibility")
        ren.converter.Y_asm("lumminance", self._runtimes)
        self._algorithm_asm(self._runtimes)


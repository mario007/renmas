
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
        max_depth = 9 
        treshold = 0.01 
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
                    hp.fliped = False
                    if hp.normal.dot(ray.dir) > 0.0:
                        hp.normal = hp.normal * -1.0
                        hp.fliped = True
                    hp.specular = 0
                    spectrum = shader.shade(hp)

                    L = L + spectrum.mix_spectrum(path)
                    Y = conv.Y(path)
                    #print(cur_depth, Y)
                    if cur_depth >= max_depth or Y < treshold: 
                        film.add_sample(sam, L)
                        break
                    material = shader._materials_idx[hp.material]
                    hp.specular = 0

                    #material.next_direction(hp)
                    material.next_direction_bsdf(hp)
                    #material.f(hp)

                    path = path.mix_spectrum(hp.f_spectrum*(1.0/hp.pdf))
                    cur_depth += 1
                    
                    ray = Ray(hp.hit_point, hp.wi)
                    hp = intersector.isect(ray) 
                    if not hp: 
                        if shader.environment_light is not None:
                            le = shader.environment_light.Le(ray.dir)
                            L = L + le.mix_spectrum(path)
                            film.add_sample(sam, L)
                        else:
                            film.add_sample(sam, L)
                        break
                    
                #film.add_sample(sam, L)
            else:
                if shader.environment_light is not None:
                    film.add_sample(sam, shader.environment_light.Le(ray.dir))
                else:
                    film.add_sample(sam, background)

    def _algorithm_asm(self, runtimes):
        
        code = """
            #DATA
        """
        mat_list = self._renderer.shader._materials_lst
        label_environment = "environemtn_L" + str(abs(hash(self)))
        if self._renderer.shader.environment_light is not None:
            ren = self._renderer
            env_light = ren.shader.environment_light
            env_light.Le_asm(runtimes, ren.assembler, ren.structures, label_environment)

        code += self._renderer.structures.structs(('sample', 'ray', 'hitpoint')) + """
            sample sample1
            ray ray1
            float minus_one[4] = -1.0, -1.0, -1.0, 0.0
            float one[4] = 1.0, 1.0, 1.0, 1.0
            float zero[4] = 0.0, 0.0, 0.0, 0.0
            hitpoint hp1
            uint32 max_depth = 8
            uint32 cur_depth = 0
            spectrum path
            spectrum L
            spectrum background
            spectrum temp_spectrum
            float treshold = 0.01
            """
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
            mov dword [eax + hitpoint.fliped], 0
            macro eq128 eax.hitpoint.wo = ebx.ray.dir * minus_one {xmm0} 
            macro dot xmm1 = eax.hitpoint.normal * ebx.ray.dir {xmm5, xmm6}
            macro if xmm1 < zero goto __shade
            macro eq128 xmm0 = eax.hitpoint.normal * minus_one
            macro eq128 eax.hitpoint.normal = xmm0 {xmm1}
            mov dword [eax + hitpoint.fliped], 1
            __shade:
            mov dword [eax + hitpoint.specular], 0
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
            ; call bsdf next direction 
            mov eax, hp1 
            mov dword [eax + hitpoint.specular], 0
            mov ebx, dword [eax + hitpoint.mat_index]
            call dword [samplings + 4*ebx] 
            mov eax, hp1
            macro eq32 xmm0 = one / eax.hitpoint.pdf
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
            
        """
        if self._renderer.shader.environment_light is not None:
            code += """
            mov eax, ray1
            macro eq128 xmm0 = eax.ray.dir
            """
            code += "call " + label_environment + """ 
            mov ebx, path
            macro spectrum ebx = ebx * eax 
            mov ecx, L
            macro spectrum ecx = ecx + ebx
            """

        code += """
            _write_sample:
            mov eax, L 
            mov ebx, sample1
            call add_sample
            jmp _main_loop

            _write_background:
        """
        if self._renderer.shader.environment_light is not None:
            code += """
            mov eax, ray1
            macro eq128 xmm0 = eax.ray.dir
            """
            code += "call " + label_environment + "\n"
        else:
            code += " mov eax, background \n"

        code += """
            mov ebx, sample1 
            call add_sample
            jmp _main_loop

            _end_rendering:
            #END
        """

        ren = self._renderer
        for m in mat_list:
            m.next_direction_bsdf_asm(runtimes, ren.structures, ren.assembler)

        mc = self._renderer.assembler.assemble(code)
        #mc.print_machine_code()
        name = "pathtracer_integrator"
        self._ds = []
        for r in runtimes:
            ds = r.load(name, mc)
            self._ds.append(ds)
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

        #TODO -- allocate memory depending of the scene -- assembler support is missing for this!!!
        self._runtimes = [Runtime(code=8, data=8) for n in range(ren.threads)] 
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


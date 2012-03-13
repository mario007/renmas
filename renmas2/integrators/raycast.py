
import x86
from tdasm import Runtime
from .integrator import Integrator 
from ..core import Spectrum
from ..shapes import HitPoint

class Raycast(Integrator):
    def __init__(self, renderer):
        super(Raycast, self).__init__(renderer)
        self._ds = None

    def render_py(self, tile):
        ren = self._renderer
        sampler = ren.sampler
        sampler.set_tile(tile)
        camera = ren.camera
        intersector = ren.intersector
        film = ren.film
        shader = ren.shader

        background = ren.converter.create_spectrum((0.70, 0.0, 0.0))

        while True:
            sam = sampler.get_sample()
            if sam is None: break 
            ray = camera.ray(sam) 
            hp = intersector.isect(ray) 
            if hp:
                hp.wo = ray.dir * -1.0
                spectrum = shader.shade(hp)
                film.add_sample(sam, spectrum)
            else:
                film.add_sample(sam, background)

    def _algorithm_asm(self, runtimes):
        
        code = """
            #DATA
        """
        code += self._renderer.structures.structs(('sample', 'ray', 'hitpoint')) + """
            sample sample1
            ray ray1
            float minus_one[4] = -1.0, -1.0, -1.0, 0.0
            float zero = 0.0
            hitpoint hp1
            spectrum background

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

            ; call shading routine
            mov eax, hp1
            mov ebx, ray1 
            macro eq128 eax.hitpoint.wo = ebx.ray.dir * minus_one {xmm0} 
            macro dot xmm1 = eax.hitpoint.normal * ebx.ray.dir {xmm5, xmm6}
            macro if xmm1 < zero goto __shade
            macro eq128 xmm0 = eax.hitpoint.normal * minus_one
            macro eq128 eax.hitpoint.normal = xmm0 {xmm1}
            __shade:
            call shade

            mov ecx, hp1
            lea eax, dword [ecx + hitpoint.l_spectrum]
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

        mc = self._renderer.assembler.assemble(code)
        #mc.print_machine_code()
        name = "raycast_integrator"
        self._ds = []
        for r in runtimes:
            self._ds.append(r.load(name, mc))

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
            addrs.append(r.address_module('raycast_integrator'))

        x86.ExecuteModules(tuple(addrs))

    def prepare(self):
        ren = self._renderer
        self._background = ren.converter.create_spectrum((0.70, 0.0, 0.0))

        self._runtimes = [Runtime() for n in range(ren.threads)] 
        ren.macro_call.set_runtimes(self._runtimes)
        ren.sampler.get_sample_asm(self._runtimes, 'get_sample', ren.assembler, ren.structures)
        ren.camera.ray_asm(self._runtimes, 'get_ray', ren.assembler, ren.structures)
        ren.intersector.isect_asm(self._runtimes, 'ray_scene_intersection')
        ren.converter.to_rgb_asm("spectrum_to_rgb", self._runtimes)
        ren.film.add_sample_asm(self._runtimes, "add_sample", "spectrum_to_rgb")
        ren.intersector.visibility_asm(self._runtimes, "ray_scene_visibility")
        ren.shader.shade_asm(self._runtimes, "shade", "ray_scene_visibility")
        self._algorithm_asm(self._runtimes)


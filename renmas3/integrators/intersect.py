
import time
import x86
from tdasm import Runtime
from .integrator import Integrator 
from ..core import Spectrum, ShadePoint, Ray
from ..samplers import Sample

class IsectIntegrator(Integrator):
    def __init__(self, renderer):
        super(IsectIntegrator, self).__init__(renderer)
        self._ds = None

    def render_py(self, tile):
        ren = self._renderer
        sampler = ren.sampler
        sampler.set_tile(tile)
        camera = ren.camera
        intersector = ren.shape_mgr
        film = ren.film
        background = ren.color_mgr.create_spectrum((0.70, 0.0, 0.0))
        foreground = ren.color_mgr.create_spectrum((0.0, 0.70, 0.0))
        
        while True:
            sam = sampler.get_sample()
            if sam is None: break 
            ray = camera.ray(sam) 
            hp = intersector.isect(ray) 
            if hp:
                film.add_sample(sam, foreground)
            else:
                film.add_sample(sam, background)

    def render_asm(self, tile):
        self._renderer.sampler.set_tile(tile)
        runtimes = self._runtimes
        
        addrs = []
        for i in range(len(tile.lst_tiles)):
            r = runtimes[i]
            addrs.append(r.address_module('isect_integrator'))

        x86.ExecuteModules(tuple(addrs))

    def prepare(self):
        ren = self._renderer
        self._background = ren.color_mgr.create_spectrum((0.70, 0.0, 0.0))
        self._foreground = ren.color_mgr.create_spectrum((0.0, 0.70, 0.0))

        self._runtimes = [Runtime() for n in range(ren.threads)] 
        ren.macro_call.set_runtimes(self._runtimes)
        ren.sampler.get_sample_asm(self._runtimes, 'get_sample', ren.assembler)
        ren.camera.ray_asm(self._runtimes, 'get_ray', ren.assembler)
        ren.shape_mgr.isect_asm(self._runtimes, 'ray_scene_intersection')
        ren.film.add_sample_asm(self._runtimes, "add_sample")
        self._algorithm_asm(self._runtimes)

    def _algorithm_asm(self, runtimes):
        ren = self._renderer
        
        code = """
            #DATA
        """
        code += ren.color_mgr.spectrum_struct() + Ray.struct() + Sample.struct() + ShadePoint.struct() + """  
            sample sample1
            ray ray1
            shadepoint hp1
            spectrum background
            spectrum foreground

            #CODE
            _main_loop:
            macro mov eax, sample1
            call get_sample
            cmp eax, 0
            je _end_rendering

            macro mov eax, sample1
            macro mov ebx, ray1
            call get_ray

            ; eax = pointer_to_ray, ebx = pointer_to_hitpoint
            macro mov eax, ray1 
            macro mov ebx, hp1 
            call ray_scene_intersection 

            cmp eax, 0
            je _write_background

            macro mov eax, foreground 
            macro mov ebx, sample1 
            call add_sample
            jmp _main_loop

            _write_background:
            macro mov eax, background 
            macro mov ebx, sample1 
            call add_sample

            jmp _main_loop

            _end_rendering:
            #END
        """

        mc = self._renderer.assembler.assemble(code)
        #mc.print_machine_code()
        name = "isect_integrator"
        self._ds = []
        for r in runtimes:
            self._ds.append(r.load(name, mc))

        self._populate_ds()

    def _populate_ds(self):
        if self._ds is None: return
        for ds in self._ds:
            ds['background.values'] = self._background.to_ds()
            ds['foreground.values'] = self._foreground.to_ds() 
    

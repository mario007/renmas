

import x86
from tdasm import Runtime
from .integrator import Integrator 
from ..core import Spectrum
from ..shapes import HitPoint

class IsectIntegrator(Integrator):
    def __init__(self, renderer):
        super(IsectIntegrator, self).__init__(renderer)
        self._ds = None

    def render_py(self, tile):
        sampler = self._renderer._sampler
        sampler.set_tile(tile)
        camera = self._renderer._camera
        intersector = self._renderer._intersector
        film = self._renderer._film

        background = Spectrum(False, (0.99, 0.0, 0.0))
        foreground = Spectrum(False, (0.0, 0.99, 0.0))
        hp1 = HitPoint()
        hp2 = HitPoint()
        hp1.spectrum = background
        hp2.spectrum = foreground

        while True:
            sam = sampler.get_sample()
            if sam is None: break 
            ray = camera.ray(sam) 
            hp = intersector.isect(ray) 
            if hp:
                film.add_sample(sam, hp2)
            else:
                film.add_sample(sam, hp1)

    def render_asm(self, tile):
        self._renderer._sampler.set_tile(tile)
        runtimes = self._runtimes
        
        addrs = []
        for i in range(len(tile.lst_tiles)):
            r = runtimes[i]
            addrs.append(r.address_module('isect_integrator'))

        x86.ExecuteModules(tuple(addrs))

    def prepare(self):
        self._runtimes = [Runtime() for n in range(self._renderer._threads)] 
        ren = self._renderer
        ren.macro_call.set_runtimes(self._runtimes)
        self._renderer._sampler.get_sample_asm(self._runtimes, 'get_sample', ren.assembler, ren.structures)
        self._renderer._camera.ray_asm(self._runtimes, 'get_ray', ren.assembler, ren.structures)
        self._renderer._intersector.isect_asm(self._runtimes, 'ray_scene_intersection', ren.assembler, ren.structures)
        self._renderer._film.add_sample_asm(self._runtimes, 'add_sample', ren.assembler, ren.structures)
        self._algorithm_asm(self._runtimes, ren.assembler, ren.structures)

    def _algorithm_asm(self, runtimes, assembler, structures):
        
        code = """
            #DATA
        """
        code += structures.structs(('sample', 'ray', 'hitpoint')) + """
            sample sample1
            ray ray1
            hitpoint hp1
            hitpoint background
            hitpoint foreground
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

            mov eax, foreground 
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

        mc = assembler.assemble(code)
        #mc.print_machine_code()
        name = "isect_integrator"
        self._ds = []
        for r in runtimes:
            self._ds.append(r.load(name, mc))

        self._populate_ds()

    def _populate_ds(self):
        if self._ds is None: return
        for ds in self._ds:
            ds['background.spectrum'] = (0.99, 0.0, 0.0, 0.0)
            ds['foreground.spectrum'] = (0.0, 0.99, 0.0, 0.0)
    

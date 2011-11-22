

import x86
from tdasm import Runtime
from .integrator import Integrator 
from ..core import get_structs, Spectrum
from ..macros import macro_call, assembler
from ..shapes import HitPoint

class IsectIntegrator(Integrator):
    def __init__(self, renderer):
        super(IsectIntegrator, self).__init__(renderer)

    def render_py(self, tile):
        sampler = self._renderer._sampler
        sampler.set_tile(tile)
        camera = self._renderer._camera
        intersector = self._renderer._intersector
        film = self._renderer._film

        background = Spectrum(0.99, 0.0, 0.0)
        foreground = Spectrum(0.0, 0.99, 0.0)
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
        self._renderer._sampler.get_sample_asm(self._runtimes, 'get_sample')
        self._renderer._camera.ray_asm(self._runtimes, 'get_ray')
        self._renderer._intersector.isect_asm(self._runtimes, 'ray_scene_intersection')
        self._algorithm_asm(self._runtimes)

    def _algorithm_asm(self, runtimes):
        
        code = """
            #DATA
        """
        code += get_structs(('sample', 'ray', 'hitpoint')) + """
            sample sample1
            ray ray1
            hitpoint hp1
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

            jmp _main_loop

            _end_rendering:
            #END
        """

        macro_call.set_runtimes(runtimes)
        mc = assembler.assemble(code)
        #mc.print_machine_code()
        name = "isect_integrator"
        self._ds = []
        for r in runtimes:
            self._ds.append(r.load(name, mc))

    

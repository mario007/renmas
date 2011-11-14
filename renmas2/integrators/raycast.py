
import x86
from ..core import get_structs
from ..macros import macro_call, assembler

class Raycast:
    def __init__(self, renderer):
        self._renderer = renderer
        self._asm = False
        self._ds = None

    def asm(self, flag):
        self._asm = bool(flag)

    def render(self, tile):
        if self._asm:
            self.render_asm(tile)
        else:
            self.render_asm(tile)
            #self.render_py(tile)

    def render_py(self, tile):
        sampler = self._renderer._get_sampler()
        sampler.set_tile(tile)

        while True:
            sam = sampler.get_sample()
            if sam is None: break 

    def render_asm(self, tile):
        sampler = self._renderer._get_sampler()
        sampler.set_tile(tile)
        runtimes = self._renderer._runtimes
        
        addrs = []
        for i in range(len(tile.lst_tiles)):
            r = runtimes[i]
            addrs.append(r.address_module('raycast_integrator'))

        x86.ExecuteModules(tuple(addrs))

    def algorithm_asm(self, runtimes):
        pass
        
        code = """
            #DATA
        """
        code += get_structs(('sample',)) + """
            sample sample1
            #CODE
            _main_loop:
            mov eax, sample1
            call get_sample
            cmp eax, 0
            je _end_rendering

            jmp _main_loop

            _end_rendering:
            #END
        """

        macro_call.set_runtimes(runtimes)
        mc = assembler.assemble(code)
        #mc.print_machine_code()
        name = "raycast_integrator"
        self._ds = []
        for r in runtimes:
            self._ds.append(r.load(name, mc))

    

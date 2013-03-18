from tdasm import Tdasm, Runtime

from .powps import pow_ps_asm
from .powss import pow_ss_asm

_asm_functions = {}
_asm_functions['pow_ps'] = pow_ps_asm 
_asm_functions['pow_ss'] = pow_ss_asm

_compiled_funs ={}

# load_asm_function(sin, fast_sin_bbfdsf, runtimes)

def load_asm_function(name, label, runtimes, AVX=False, BIT64=False):

    if len(_compiled_funs) > 200: #clear cache
        _compiled_funs.clear()

    typ = (name, label, AVX, BIT64)
    if typ in _compiled_funs:
        mc = _compiled_funs[typ]
    else:
        if name not in _asm_functions:
            raise ValueError("Asm function %s doesnt exist!" % name)
        code = _asm_functions[name](label, AVX, BIT64)
        asm = Tdasm()
        mc = asm.assemble(code, True)
    
    for r in runtimes:
        if not r.global_exists(label):
            name = label + str(id(typ))
            r.load(name, mc)


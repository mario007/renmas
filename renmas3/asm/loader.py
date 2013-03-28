import random
from tdasm import Tdasm, Runtime

from ..macros import create_assembler
from .powps import pow_ps_asm
from .powss import pow_ss_asm
from .logps import log_ps_asm
from .logss import log_ss_asm
from .expps import exp_ps_asm
from .expss import exp_ss_asm
from .sincosps import sincos_ps_asm
from .random_float import random_float
from .hemisphere import sample_hemisphere_asm

_asm_functions = {}
_asm_functions['pow_ps'] = pow_ps_asm 
_asm_functions['pow_ss'] = pow_ss_asm
_asm_functions['log_ps'] = log_ps_asm 
_asm_functions['log_ss'] = log_ss_asm
_asm_functions['exp_ps'] = exp_ps_asm
_asm_functions['exp_ss'] = exp_ss_asm
_asm_functions['random'] = random_float
_asm_functions['sincos_ps'] = sincos_ps_asm
_asm_functions['sample_hemisphere'] = sample_hemisphere_asm

_compiled_funs ={}

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
        if isinstance(code, tuple):
            code, funcs = code
            for fun in funcs:
                fun_name, fun_label = fun
                load_asm_function(fun_name, fun_label, runtimes, AVX, BIT64)
        asm = create_assembler()
        mc = asm.assemble(code, True)
    
    for r in runtimes:
        if not r.global_exists(label):
            mod_name = label + str(id(typ))
            ds = r.load(mod_name, mc)
            if name in ('random', 'random2', 'random3', 'random4'):
                v1 = random.randint(0, 4000000000) 
                v2 = random.randint(0, 4000000000) 
                v3 = random.randint(0, 4000000000) 
                v4 = random.randint(0, 4000000000) 
                ds['cur_seed'] = (v1, v2, v3, v4) 


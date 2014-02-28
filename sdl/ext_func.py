
from tdasm import iset_supported
from tdasm.asm_lib import logss, logps, expss, expps, powss, powps, rnd


class ExtFunction:
    def __init__(self, name, label, AVX, ia32):
        self.name = name
        self.label = label
        self.AVX = AVX
        self.ia32 = ia32


def load_ext_function(runtimes, ext_func):
    funcs = {}
    funcs['log_ss'] = logss.log_ss_asm
    funcs['log_ps'] = logps.log_ps_asm
    funcs['exp_ss'] = expss.exp_ss_asm
    funcs['exp_ps'] = expps.exp_ps_asm
    funcs['pow_ss'] = powss.pow_ss_asm
    funcs['pow_ps'] = powps.pow_ps_asm

    if ext_func.name in ('rand_int', 'random', 'random2', 'random3', 'random4'):
        if ext_func.name == 'rand_int':
            rnd.rand_int(runtimes, ext_func.label, AVX=ext_func.AVX,
                         ia32=ext_func.ia32, hardware=iset_supported('rdrand'))
        else:
            rnd.rand_float(runtimes, ext_func.label, AVX=ext_func.AVX,
                           ia32=ext_func.ia32, hardware=iset_supported('rdrand'))
        return

    name = ext_func.name
    if name not in funcs:
        raise ValueError("External function %s doesn't exist!" % name)

    label = ext_func.label
    AVX = ext_func.AVX
    ia32 = ext_func.ia32
    funcs[name](runtimes, label, AVX=AVX, ia32=ia32)

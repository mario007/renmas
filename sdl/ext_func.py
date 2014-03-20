
from tdasm import iset_supported
from tdasm.asm_lib import logss, logps, expss, expps, powss, powps,\
    acosss, acosps, asinss, asinps, atanps, atanss, atanr2ps,\
    atanr2ss, cosps, cosss, sinps, sinss, tanps, tanss, rnd


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
    funcs['acos_ss'] = acosps.acos_ps_asm  # there is bug in acosss for negative values
    funcs['acos_ps'] = acosps.acos_ps_asm
    funcs['asin_ss'] = asinss.asin_ss_asm
    funcs['asin_ps'] = asinps.asin_ps_asm
    funcs['atan_ss'] = atanss.atan_ss_asm
    funcs['atan_ps'] = atanps.atan_ps_asm
    funcs['atanr2_ss'] = atanr2ss.atanr2_ss_asm
    funcs['atanr2_ps'] = atanr2ps.atanr2_ps_asm
    funcs['cos_ss'] = cosss.cos_ss_asm
    funcs['cos_ps'] = cosps.cos_ps_asm
    funcs['sin_ss'] = sinss.sin_ss_asm
    funcs['sin_ps'] = sinps.sin_ps_asm
    funcs['tan_ss'] = tanss.tan_ss_asm
    funcs['tan_ps'] = tanps.tan_ps_asm

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

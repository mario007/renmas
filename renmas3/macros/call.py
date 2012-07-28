
import random
from functools import partial
from tdasm import Tdasm

from ..asm_lib import sin_ss, sin_ps, cos_ss, cos_ps, sincos_ss, sincos_ps, exp_ss, exp_ps, pow_ss, pow_ps
from ..asm_lib import atan_ss, atan_ps, asin_ss, asin_ps, acos_ss, acos_ps, tan_ss, tan_ps, log_ss, log_ps
from ..asm_lib import atanr2_ps, atanr2_ss
from ..asm_lib import random_float

import renmas3.switch as proc

from renmas3.macros import lea, mov, arithmetic32, arithmetic128,\
                            broadcast, macro_if, dot_product, normalization, cross_product

def create_assembler():
    assembler = Tdasm()
    assembler.register_macro('mov', mov)
    assembler.register_macro('lea', lea)
    assembler.register_macro('eq128', arithmetic128)
    assembler.register_macro('eq32', arithmetic32)
    assembler.register_macro('broadcast', broadcast)
    assembler.register_macro('if', macro_if)
    assembler.register_macro('dot', dot_product)
    assembler.register_macro('normalization', normalization)
    assembler.register_macro('cross', cross_product)
    return assembler

#from renmas2.utils import reflect_asm, tir_asm, refract_asm

# caching asm library  
class MacroCall:
    def __init__(self):
        
        self._compiled_code = {} # compiled functions 
        self._funcs_to_load = [] # lazy loading of functions
        self._color_mgr = None 

        self._runtimes = None
        self.assembler = create_assembler()
        self.assembler.register_macro('call', self.macro_call)

        self.functions = {}
        self.functions['fast_sin_ss'] = sin_ss 
        self.functions['fast_sin_ps'] = sin_ps
        self.functions['fast_cos_ss'] = cos_ss
        self.functions['fast_cos_ps'] = cos_ps
        self.functions['fast_sincos_ss'] = sincos_ss
        self.functions['fast_sincos_ps'] = sincos_ps
        self.functions['fast_exp_ss'] = exp_ss
        self.functions['fast_exp_ps'] = exp_ps
        self.functions['fast_pow_ss'] = pow_ss
        self.functions['fast_pow_ps'] = pow_ps
        self.functions['fast_atan_ss'] = atan_ss
        self.functions['fast_atan_ps'] = atan_ps
        self.functions['fast_asin_ss'] = asin_ss
        self.functions['fast_asin_ps'] = asin_ps
        self.functions['fast_acos_ss'] = acos_ss
        self.functions['fast_acos_ps'] = acos_ps
        self.functions['fast_tan_ss'] = tan_ss
        self.functions['fast_tan_ps'] = tan_ps
        self.functions['fast_log_ss'] = log_ss
        self.functions['fast_log_ps'] = log_ps
        self.functions['fast_atanr2_ps'] = atanr2_ps
        self.functions['fast_atanr2_ss'] = atanr2_ss
        self.functions['random'] = random_float
        #self.functions['reflect'] = partial(reflect_asm, self.assembler)
        #self.functions['refract'] = partial(refract_asm, self.assembler)
        #self.functions['tir'] = partial(tir_asm, self.assembler)
        

        self.inline_macros = {} #normalization, cross product etc...
        self.inline_macros['int_to_float'] = self.int_to_float
        self.inline_macros['float_to_int'] = self.float_to_int
        self.inline_macros['sqrtss'] = self.sqrtss
        self.inline_macros['set_pixel'] = self.set_pixel
        self.inline_macros['zero'] = self.zero_register
        self.inline_macros['minps'] = self.minps
        self.inline_macros['maxps'] = self.maxps
        self.inline_macros['minss'] = self.minss
        self.inline_macros['maxss'] = self.maxss
        self.inline_macros['andps'] = self.andps
        self.inline_macros['cmpps'] = self.cmpps
        self.inline_macros['orps'] = self.orps

    # first token is name of function
    # if inline is specified it must be second token [inline is optional]
    # rest of tokens are arguments to function
    # function can also be inline even if inline modifier is not specified

    def macro_call(self, asm, tokens):
        if len(tokens) == 0: return
        func_name = tokens[0]

        if func_name in self.inline_macros:
            return self.inline_macros[func_name](asm, tokens[1:])
        
        if func_name == 'random':
            self._load_random()
            return 'call ' + func_name
        elif func_name in self.functions:
            self._load_func(func_name)
            return 'call ' + func_name
        elif func_name in ('XYZ_to_RGB', 'lumminance', 'spectrum_to_rgb'):
            self._load_spectrum_func(func_name)
            return 'call ' + func_name
        else:
            raise ValueError('Unknown function!!!')

    def set_color_mgr(self, mgr):
        self._color_mgr = mgr

    def set_runtimes(self, runtimes):
        self._runtimes = runtimes
        for f in self._funcs_to_load:
            if f == 'random':
                self._load_random()
            else:
                self._load_func(f)

    def _load_func(self, func_name):
        if self._runtimes is None: 
            raise ValueError('Runtime does not exist!!!')

        if func_name not in self._compiled_code:
            self._compiled_code[func_name] = self.functions[func_name]()

        for runtime in self._runtimes:
            if not runtime.global_exists(func_name):
                runtime.load(func_name, self._compiled_code[func_name])

        if func_name not in self._funcs_to_load:
            self._funcs_to_load.append(func_name)
    
    def _load_spectrum_func(self, func_name):
        if self._color_mgr is None:
            raise ValueError('Color manager is not set!!!')
        
        if func_name == 'XYZ_to_RGB':
            self._color_mgr.XYZ_to_RGB_asm(self._runtimes)
        elif func_name == 'lumminance':
            self._color_mgr.Y_asm(self._runtimes)
        elif func_name == 'spectrum_to_rgb':
            self._color_mgr.to_RGB_asm(self._runtimes)

    def _load_random(self):
        if 'random' not in self._compiled_code:
            self._compiled_code['random'] = self.functions['random']()

        if self._runtimes is None: 
            raise ValueError('Runtime does not exist!!!')
        for runtime in self._runtimes:
            if not runtime.global_exists('random'):
                ds = runtime.load('random_float', self._compiled_code['random'])
                v1 = random.randint(0, 4000000000) 
                v2 = random.randint(0, 4000000000) 
                v3 = random.randint(0, 4000000000) 
                v4 = random.randint(0, 4000000000) 
                ds['cur_seed'] = (v1, v2, v3, v4) 

        if 'random' not in self._funcs_to_load:
            self._funcs_to_load.append('random')

    def int_to_float(self, asm, tokens):
        xmm1, dummy, xmm2 = tokens
        if proc.AVX:
            return 'vcvtdq2ps ' + xmm1 + ' , ' + xmm2 + '\n'
        else:
            return 'cvtdq2ps ' + xmm1 + ' , ' + xmm2 + '\n'

    def float_to_int(self, asm, tokens):
        xmm1, dummy, xmm2 = tokens
        if proc.AVX:
            return 'vcvtps2dq ' + xmm1 + ' , ' + xmm2 + '\n'
        else:
            return 'cvtps2dq ' + xmm1 + ' , ' + xmm2 + '\n'

    def sqrtss(self, asm, tokens):
        xmm1, dummy, xmm2 = tokens
        if proc.AVX:
            return 'vsqrtss ' + xmm1 + ',' + xmm1 + ',' + xmm2 + '\n'
        else:
            return 'sqrtss ' + xmm1 + ',' + xmm2 + '\n'

    def minps(self, asm, tokens):
        xmm1, dummy, xmm2 = tokens
        if proc.AVX:
            return 'vminps ' + xmm1 + ',' + xmm1 + ',' + xmm2 + '\n'
        else:
            return 'minps ' + xmm1 + ',' + xmm2 + '\n'

    def minss(self, asm, tokens):
        xmm1, dummy, xmm2 = tokens
        if proc.AVX:
            return 'vminss ' + xmm1 + ',' + xmm1 + ',' + xmm2 + '\n'
        else:
            return 'minss ' + xmm1 + ',' + xmm2 + '\n'

    def maxps(self, asm, tokens):
        xmm1, dummy, xmm2 = tokens
        if proc.AVX:
            return 'vmaxps ' + xmm1 + ',' + xmm1 + ',' + xmm2 + '\n'
        else:
            return 'maxps ' + xmm1 + ',' + xmm2 + '\n'

    def maxss(self, asm, tokens):
        xmm1, dummy, xmm2 = tokens
        if proc.AVX:
            return 'vmaxss ' + xmm1 + ',' + xmm1 + ',' + xmm2 + '\n'
        else:
            return 'maxss ' + xmm1 + ',' + xmm2 + '\n'

    def cmpps(self, asm, tokens):
        xmm1, dummy, xmm2, dummy2, num = tokens
        if proc.AVX:
            return 'vcmpps ' + xmm1 + ',' + xmm1 + ',' + xmm2 + ',' + num + '\n'
        else:
            return 'cmpps ' + xmm1 + ',' + xmm2 + ',' + num +'\n'

    def andps(self, asm, tokens):
        xmm1, dummy, xmm2 = tokens
        if proc.AVX:
            return 'vandps ' + xmm1 + ',' + xmm1 + ',' + xmm2 + '\n'
        else:
            return 'andps ' + xmm1 + ',' + xmm2 + '\n'

    def orps(self, asm, tokens):
        xmm1, dummy, xmm2 = tokens
        if proc.AVX:
            return 'vorps ' + xmm1 + ',' + xmm1 + ',' + xmm2 + '\n'
        else:
            return 'orps ' + xmm1 + ',' + xmm2 + '\n'

    def zero_register(self, asm, tokens):
        xmm = tokens[0]
        if proc.AVX:
            return 'vpxor ' + xmm + ',' + xmm + ',' + xmm + '\n'
        else:
            return 'pxor ' + xmm + ',' + xmm + '\n'

    def set_pixel(self, asm, tokens):
        # eax = x , ebx = y, esi = ptr_image, edx = pitch value = xmm0
        asm_code = """
            imul ebx, edx 
            imul eax, eax, 16
            add  eax, ebx
            add eax, esi 
        """
        if proc.AVX:
            line = "vmovaps oword [eax], xmm0"
        else:
            line = "movaps oword [eax], xmm0"
        return asm_code + line

import renmas3.core

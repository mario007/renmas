
from ..asm_library import sin_ss, sin_ps, cos_ss, cos_ps, sincos_ss, sincos_ps, exp_ss, exp_ps, pow_ss, pow_ps
from ..asm_library import atan_ss, atan_ps, asin_ss, asin_ps, acos_ss, acos_ps, tan_ss, tan_ps, log_ss, log_ps
from ..asm_library import random_float
import random
import renmas2.switch as proc

# caching asm library  
class MacroCall:
    def __init__(self):
        
        self.compiled_code = {} # 
        self.runtime_arr = None

        self.functions = {}
        self.functions['fast_exp_ss'] = exp_ss
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
        self.functions['random'] = random_float
        


        self.inline_macros = {} #normalization, cross product etc...
        self.inline_macros['int_to_float'] = self.int_to_float
        self.inline_macros['sqrtss'] = self.sqrtss
        self.inline_macros['set_pixel'] = self.set_pixel

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
        if func_name in self.compiled_code:
            self._load_func(func_name)
            return 'call ' + func_name
        elif func_name in self.functions:
            self.compiled_code[func_name] = self.functions[func_name]()
            self._load_func(func_name)
            return 'call ' + func_name
        else:
            raise ValueError('Unknown function!!!')

    def set_runtimes(self, runtime_arr):
        self.runtime_arr = runtime_arr

    def _load_func(self, func_name):
        if self.runtime_arr is None: 
            raise ValueError('Runtime does not exist!!!')
        for runtime in self.runtime_arr:
            if not runtime.global_exists(func_name):
                runtime.load(func_name, self.compiled_code[func_name])

    def _load_random(self):
        if 'random' not in self.compiled_code:
            self.compiled_code['random'] = self.functions['random']()

        if self.runtime_arr is None: 
            raise ValueError('Runtime does not exist!!!')
        for runtime in self.runtime_arr:
            if not runtime.global_exists('random'):
                ds = runtime.load('random_float', self.compiled_code['random'])
                v1 = random.randint(0, 4000000000) 
                v2 = random.randint(0, 4000000000) 
                v3 = random.randint(0, 4000000000) 
                v4 = random.randint(0, 4000000000) 
                ds['cur_seed'] = (v1, v2, v3, v4) 


    def int_to_float(self, asm, tokens):
        xmm1, dummy, xmm2 = tokens
        if proc.AVX:
            return 'vcvtdq2ps ' + xmm1 + ' , ' + xmm2 + '\n'
        else:
            return 'cvtdq2ps ' + xmm1 + ' , ' + xmm2 + '\n'

    def sqrtss(self, asm, tokens):
        xmm1, dummy, xmm2 = tokens
        if proc.AVX:
            return 'vsqrtss ' + xmm1 + ',' + xmm1 + ',' + xmm2 + '\n'
        else:
            return 'sqrtss ' + xmm1 + ',' + xmm2 + '\n'

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


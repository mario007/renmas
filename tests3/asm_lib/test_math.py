
import unittest
from math import sin, cos, exp, atan, asin, acos, tan, log, atan2
from random import random

from tdasm import Tdasm, Runtime
from renmas3.macros import MacroCall

def asm_code(func_name):
    code = """
    #DATA
    float v1[4]
    float v2[4]
    #CODE
    movaps xmm0, oword [v1]
    movaps xmm1, oword [v2]
    """
    code += "macro call " + func_name + """
    movaps oword [v1], xmm0 
    movaps oword [v2], xmm6
    #END
    """
    return code

class TestTrigs(unittest.TestCase):
    def setUp(self):
        self.runtime = Runtime()
        self.macro_call = MacroCall()
        self.macro_call.set_runtimes([self.runtime])
        self.assembler = Tdasm()
        self.assembler.register_macro('call', self.macro_call.macro_call)
    
    def check_seq(self, seq1, seq2, precision):
        for x, y in zip(seq1, seq2):
            self.assertAlmostEqual(x, y, precision)

    def ss_test(self, func_name, func, precision=3, negative=True):
        mc = self.assembler.assemble(asm_code(func_name))
        ds = self.runtime.load('test_fun', mc)

        for x in range(100):
            if negative:
                num = (random() - 0.5) * 2 
            else:
                num = random()
            ds["v1"] = (num, num, num, num) 
            self.runtime.run("test_fun")
            rez_asm = ds["v1"][0]
            self.assertAlmostEqual(rez_asm, func(num), precision)

    def ps_test(self, func_name, func, precision=3, negative=True):
        mc = self.assembler.assemble(asm_code(func_name))
        ds = self.runtime.load('test_fun', mc)

        for x in range(100):
            if negative:
                num1, num2, num3, num4  = [(random() - 0.5)*2 for i in range(4)]
            else:
                num1, num2, num3, num4 = random(), random(), random(), random()
            ds["v1"] = (num1, num2, num3, num4) 
            self.runtime.run("test_fun")
            rez_asm = ds["v1"]
            self.check_seq(rez_asm, [func(num1), func(num2), func(num3), func(num4)], precision)

    def test_sin(self):
        self.ss_test('fast_sin_ss', sin)

    def test_sin_ps(self):
        self.ps_test('fast_sin_ps', sin)

    def test_cos(self):
        self.ss_test('fast_cos_ss', cos)

    def test_cos_ps(self):
        self.ps_test('fast_cos_ps', cos)
    
    def test_exp(self):
        self.ss_test('fast_exp_ss', exp)

    def test_exp_ps(self):
        self.ps_test('fast_exp_ps', exp)

    def test_atan(self):
        self.ss_test('fast_atan_ss', atan)

    def test_atan_ps(self):
        self.ps_test('fast_atan_ps', atan)

    def test_asin(self):
        self.ss_test('fast_asin_ss', asin)

    def test_asin_ps(self):
        self.ps_test('fast_asin_ps', asin)

    def test_acos(self): # FIXME function calculate wrong result for negative numbers
        self.ss_test('fast_acos_ss', acos, precision=2, negative=False)

    def test_acos_ps(self):
        self.ps_test('fast_acos_ps', acos, precision=2)

    def test_tan(self):
        self.ss_test('fast_tan_ss', tan)

    def test_tan_ps(self):
        self.ps_test('fast_tan_ps', tan)

    def test_log(self):
        self.ss_test('fast_log_ss', log, negative=False)

    def test_log_ps(self):
        self.ps_test('fast_log_ps', log, negative=False)
    
    def test_pow_ss(self):
        mc = self.assembler.assemble(asm_code('fast_pow_ss'))
        ds = self.runtime.load('test_fun', mc)
        for x in range(100):
            num = random()
            ds["v1"] = (num, num, num, num) 
            num2 = (random() - 0.5) * 2
            ds["v2"] = (num2, num2, num2, num2) 
            self.runtime.run("test_fun")
            rez_asm = ds["v1"][0]
            self.assertAlmostEqual(rez_asm, pow(num, num2), 2)

    def test_pow_ps(self):
        mc = self.assembler.assemble(asm_code('fast_pow_ps'))
        ds = self.runtime.load('test_fun', mc)
        for x in range(100):
            num1, num2, num3, num4 = random(), random(), random(), random()
            ds["v1"] = (num1, num2, num3, num4) 
            num5, num6, num7, num8  = [(random() - 0.5)*2 for i in range(4)]
            ds["v2"] = (num5, num6, num7, num8) 
            self.runtime.run("test_fun")
            rez_asm = ds["v1"]
            self.check_seq(rez_asm, [pow(num1, num5), pow(num2, num6), pow(num3, num7), pow(num4, num8)], 2)

    def test_atanr2_ss(self):
        mc = self.assembler.assemble(asm_code('fast_atanr2_ss'))
        ds = self.runtime.load('test_fun', mc)
        for x in range(100):
            num = (random() - 0.5) * 2
            ds["v1"] = (num, num, num, num) 
            num2 = (random() - 0.5) * 2
            ds["v2"] = (num2, num2, num2, num2) 
            self.runtime.run("test_fun")
            rez_asm = ds["v1"][0]
            self.assertAlmostEqual(rez_asm, atan2(num, 1.0/num2), 2)

    def test_atanr2_ps(self):
        mc = self.assembler.assemble(asm_code('fast_atanr2_ps'))
        ds = self.runtime.load('test_fun', mc)
        for x in range(100):
            num1, num2, num3, num4  = [(random() - 0.5)*2 for i in range(4)]
            ds["v1"] = (num1, num2, num3, num4) 
            num5, num6, num7, num8  = [(random() - 0.5)*2 for i in range(4)]
            ds["v2"] = (num5, num6, num7, num8) 
            self.runtime.run("test_fun")
            rez_asm = ds["v1"]
            self.check_seq(rez_asm, [atan2(num1, 1.0/num5), atan2(num2, 1.0/num6), atan2(num3, 1.0/num7), atan2(num4, 1.0/num8)], 2)

    def test_sincos_ss(self):
        mc = self.assembler.assemble(asm_code('fast_sincos_ss'))
        ds = self.runtime.load('test_fun', mc)
        for x in range(100):
            num = (random() - 0.5) * 2
            ds["v1"] = (num, num, num, num) 
            self.runtime.run("test_fun")
            sin_asm = ds["v1"][0]
            cos_asm = ds["v2"][0]

            self.assertAlmostEqual(sin_asm, sin(num), 2)
            self.assertAlmostEqual(cos_asm, cos(num), 2)

    def test_sincos_ps(self):
        mc = self.assembler.assemble(asm_code('fast_sincos_ps'))
        ds = self.runtime.load('test_fun', mc)
        for x in range(100):
            num1, num2, num3, num4  = [(random() - 0.5)*2 for i in range(4)]
            ds["v1"] = (num1, num2, num3, num4) 
            self.runtime.run("test_fun")
            sin_asm = ds["v1"]
            cos_asm = ds["v2"]
            self.check_seq(sin_asm, [sin(num1), sin(num2), sin(num3), sin(num4)], 3)
            self.check_seq(cos_asm, [cos(num1), cos(num2), cos(num3), cos(num4)], 3)


if __name__ == "__main__":
    unittest.main()


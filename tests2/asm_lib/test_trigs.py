
import random
import unittest
import math
from tdasm import Runtime
import renmas2
import renmas2.macros as mac

SIN_CODE = """
#DATA
float x
#CODE
movss xmm0, dword [x]
macro call fast_sin_ss
movss dword [x], xmm0 
#END
"""

SIN_CODE_PS = """
#DATA
float v1[4]
#CODE
movaps xmm0, oword [v1]
macro call fast_sin_ps
movaps oword [v1], xmm0 
#END
"""

COS_CODE = """
#DATA
float x
#CODE
movss xmm0, dword [x]
macro call fast_cos_ss
movss dword [x], xmm0 
#END
"""

COS_CODE_PS = """
#DATA
float v1[4]
#CODE
movaps xmm0, oword [v1]
macro call fast_cos_ps
movaps oword [v1], xmm0 
#END
"""

SINCOS_CODE = """
#DATA
float x, y
#CODE
movss xmm0, dword [x]
macro call fast_sincos_ss
movss dword [x], xmm0 
movss dword [y], xmm6
#END
"""

SINCOS_CODE_PS = """
#DATA
float v1[4]
float v2[4]
#CODE
movaps xmm0, oword [v1]
macro call fast_sincos_ps
movaps oword [v1], xmm0 
movaps oword [v2], xmm6
#END
"""

EXP_CODE = """
#DATA
float x
#CODE
movss xmm0, dword [x]
macro call fast_exp_ss
movss dword [x], xmm0 
#END
"""

EXP_CODE_PS = """
#DATA
float v1[4]
#CODE
movaps xmm0, oword [v1]
macro call fast_exp_ps
movaps oword [v1], xmm0 
#END
"""

POW_CODE = """
#DATA
float x, y
#CODE
movss xmm0, dword [x]
movss xmm1, dword [y]
macro call fast_pow_ss
movss dword [x], xmm0 
#END
"""

POW_CODE_PS = """
#DATA
float v1[4]
float v2[4]
#CODE
movaps xmm0, oword [v1]
movaps xmm1, oword [v2]
macro call fast_pow_ps
movaps oword [v1], xmm0 
#END
"""

ATAN_CODE = """
#DATA
float x
#CODE
movss xmm0, dword [x]
macro call fast_atan_ss
movss dword [x], xmm0 
#END
"""

ATAN_CODE_PS = """
#DATA
float v1[4]
#CODE
movaps xmm0, oword [v1]
macro call fast_atan_ps
movaps oword [v1], xmm0 
#END
"""

ASIN_CODE = """
#DATA
float x
#CODE
movss xmm0, dword [x]
macro call fast_asin_ss
movss dword [x], xmm0 
#END
"""

ASIN_CODE_PS = """
#DATA
float v1[4]
#CODE
movaps xmm0, oword [v1]
macro call fast_asin_ps
movaps oword [v1], xmm0 
#END
"""

ACOS_CODE = """
#DATA
float x
#CODE
movss xmm0, dword [x]
macro call fast_acos_ss
movss dword [x], xmm0 
#END
"""

ACOS_CODE_PS = """
#DATA
float v1[4]
#CODE
movaps xmm0, oword [v1]
macro call fast_acos_ps
movaps oword [v1], xmm0 
#END
"""

TAN_CODE = """
#DATA
float x
#CODE
movss xmm0, dword [x]
macro call fast_tan_ss
movss dword [x], xmm0 
#END
"""

TAN_CODE_PS = """
#DATA
float v1[4]
#CODE
movaps xmm0, oword [v1]
macro call fast_tan_ps
movaps oword [v1], xmm0 
#END
"""

LOG_CODE = """
#DATA
float x
#CODE
movss xmm0, dword [x]
macro call fast_log_ss
movss dword [x], xmm0 
#END
"""

LOG_CODE_PS = """
#DATA
float v1[4]
#CODE
movaps xmm0, oword [v1]
macro call fast_log_ps
movaps oword [v1], xmm0 
#END
"""

class TestTrigs(unittest.TestCase):

    def setUp(self):
        self.runtime = Runtime()
        self.macro_call = mac.MacroCall()
        self.macro_call.set_runtimes([self.runtime])
        factory = renmas2.Factory()
        self.assembler = factory.create_assembler() 
        self.assembler.register_macro('call', self.macro_call.macro_call)

    def test_sin(self):
        mc = self.assembler.assemble(SIN_CODE)
        ds = self.runtime.load('sin', mc)

        for x in range(1000):
            num = random.random() * 2000
            ds["x"] = num 
            self.runtime.run("sin")
            rez_asm = ds["x"]
            rez_py = math.sin(num)
            self.assertAlmostEqual(rez_asm, rez_py, 3)

    def test_sin_ps(self):
        mc = self.assembler.assemble(SIN_CODE_PS)
        ds = self.runtime.load('sin_ps', mc)

        for x in range(1000):
            num1 = random.random() * 2000
            num2 = random.random() * 2000
            num3 = random.random() * 2000
            num4 = random.random() * 2000
            ds["v1"] = (num1, num2, num3, num4) 
            self.runtime.run("sin_ps")
            rez_asm = ds["v1"]
            rez_py1 = math.sin(num1)
            rez_py2 = math.sin(num2)
            rez_py3 = math.sin(num3)
            rez_py4 = math.sin(num4)

            self.assertAlmostEqual(rez_asm[0], rez_py1, 3)
            self.assertAlmostEqual(rez_asm[1], rez_py2, 3)
            self.assertAlmostEqual(rez_asm[2], rez_py3, 3)
            self.assertAlmostEqual(rez_asm[3], rez_py4, 3)

    def test_cos(self):
        mc = self.assembler.assemble(COS_CODE)
        ds = self.runtime.load('cos', mc)

        for x in range(1000):
            num = random.random() * 2000
            ds["x"] = num 
            self.runtime.run("cos")
            rez_asm = ds["x"]
            rez_py = math.cos(num)
            self.assertAlmostEqual(rez_asm, rez_py, 3)

    def test_cos_ps(self):
        mc = self.assembler.assemble(COS_CODE_PS)
        ds = self.runtime.load('cos_ps', mc)

        for x in range(1000):
            num1 = random.random() * 2000
            num2 = random.random() * 2000
            num3 = random.random() * 2000
            num4 = random.random() * 2000
            ds["v1"] = (num1, num2, num3, num4) 
            self.runtime.run("cos_ps")
            rez_asm = ds["v1"]
            rez_py1 = math.cos(num1)
            rez_py2 = math.cos(num2)
            rez_py3 = math.cos(num3)
            rez_py4 = math.cos(num4)

            self.assertAlmostEqual(rez_asm[0], rez_py1, 3)
            self.assertAlmostEqual(rez_asm[1], rez_py2, 3)
            self.assertAlmostEqual(rez_asm[2], rez_py3, 3)
            self.assertAlmostEqual(rez_asm[3], rez_py4, 3)

    def test_sincos(self):
        mc = self.assembler.assemble(SINCOS_CODE)
        ds = self.runtime.load('sincos', mc)

        for x in range(1000):
            num = random.random() * 2000
            ds["x"] = num 
            self.runtime.run("sincos")
            rez_asm1 = ds["x"]
            rez_asm2 = ds["y"]

            rez_py1, rez_py2 = math.sin(num), math.cos(num)
            self.assertAlmostEqual(rez_asm1, rez_py1, 3)
            self.assertAlmostEqual(rez_asm2, rez_py2, 3)

    def test_sincos_ps(self):
        mc = self.assembler.assemble(SINCOS_CODE_PS)
        ds = self.runtime.load('sincos_ps', mc)

        for x in range(1000):
            num1 = random.random() * 2000
            num2 = random.random() * 2000
            num3 = random.random() * 2000
            num4 = random.random() * 2000
            ds["v1"] = (num1, num2, num3, num4) 
            self.runtime.run("sincos_ps")
            rez_asm_sin = ds["v1"]
            rez_asm_cos = ds["v2"]
            rez_py1_sin = math.sin(num1)
            rez_py2_sin = math.sin(num2)
            rez_py3_sin = math.sin(num3)
            rez_py4_sin = math.sin(num4)
            rez_py1_cos = math.cos(num1)
            rez_py2_cos = math.cos(num2)
            rez_py3_cos = math.cos(num3)
            rez_py4_cos = math.cos(num4)

            self.assertAlmostEqual(rez_asm_sin[0], rez_py1_sin, 3)
            self.assertAlmostEqual(rez_asm_sin[1], rez_py2_sin, 3)
            self.assertAlmostEqual(rez_asm_sin[2], rez_py3_sin, 3)
            self.assertAlmostEqual(rez_asm_sin[3], rez_py4_sin, 3)
            self.assertAlmostEqual(rez_asm_cos[0], rez_py1_cos, 3)
            self.assertAlmostEqual(rez_asm_cos[1], rez_py2_cos, 3)
            self.assertAlmostEqual(rez_asm_cos[2], rez_py3_cos, 3)
            self.assertAlmostEqual(rez_asm_cos[3], rez_py4_cos, 3)


    def test_exp(self):
        mc = self.assembler.assemble(EXP_CODE)
        ds = self.runtime.load('exp', mc)

        for x in range(1000):
            num = random.random() * 4 
            ds["x"] = num 
            self.runtime.run("exp")
            rez_asm = ds["x"]
            rez_py = math.exp(num)
            self.assertAlmostEqual(rez_asm, rez_py, 2)

    def test_exp_ps(self):
        mc = self.assembler.assemble(EXP_CODE_PS)
        ds = self.runtime.load('exp_ps', mc)

        for x in range(1000):
            num1 = random.random() * 4 
            num2 = random.random() * 4
            num3 = random.random() * 4
            num4 = random.random() * 4
            ds["v1"] = (num1, num2, num3, num4) 
            self.runtime.run("exp_ps")
            rez_asm = ds["v1"]
            rez_py1 = math.exp(num1)
            rez_py2 = math.exp(num2)
            rez_py3 = math.exp(num3)
            rez_py4 = math.exp(num4)

            self.assertAlmostEqual(rez_asm[0], rez_py1, 2)
            self.assertAlmostEqual(rez_asm[1], rez_py2, 2)
            self.assertAlmostEqual(rez_asm[2], rez_py3, 2)
            self.assertAlmostEqual(rez_asm[3], rez_py4, 2)

    def test_pow(self):
        mc = self.assembler.assemble(POW_CODE)
        ds = self.runtime.load('pow', mc)

        for x in range(1000):
            num = random.random() * 3 
            num1 = random.random() * 3 
            ds["x"] = num 
            ds["y"] = num1 
            self.runtime.run("pow")
            rez_asm = ds["x"]
            rez_py = math.pow(num, num1)
            self.assertAlmostEqual(rez_asm, rez_py, 1)

    def test_pow_ps(self):
        mc = self.assembler.assemble(POW_CODE_PS)
        ds = self.runtime.load('pow_ps', mc)

        for x in range(1000):
            num1 = random.random() * 3 
            num2 = random.random() * 3
            num3 = random.random() * 3
            num4 = random.random() * 3
            num5 = random.random() * 3 
            num6 = random.random() * 3
            num7 = random.random() * 3
            num8 = random.random() * 3
            ds["v1"] = (num1, num2, num3, num4) 
            ds["v2"] = (num5, num6, num7, num8)
            self.runtime.run("pow_ps")
            rez_asm = ds["v1"]
            rez_py1 = math.pow(num1, num5)
            rez_py2 = math.pow(num2, num6)
            rez_py3 = math.pow(num3, num7)
            rez_py4 = math.pow(num4, num8)

            self.assertAlmostEqual(rez_asm[0], rez_py1, 1)
            self.assertAlmostEqual(rez_asm[1], rez_py2, 1)
            self.assertAlmostEqual(rez_asm[2], rez_py3, 1)
            self.assertAlmostEqual(rez_asm[3], rez_py4, 1)

    def test_atan(self):
        mc = self.assembler.assemble(ATAN_CODE)
        ds = self.runtime.load('atan', mc)

        for x in range(1000):
            num = random.random() * 2000
            ds["x"] = num 
            self.runtime.run("atan")
            rez_asm = ds["x"]
            rez_py = math.atan(num)
            self.assertAlmostEqual(rez_asm, rez_py, 3)

    def test_atan_ps(self):
        mc = self.assembler.assemble(ATAN_CODE_PS)
        ds = self.runtime.load('atan_ps', mc)

        for x in range(1000):
            num1 = random.random() * 2000
            num2 = random.random() * 2000
            num3 = random.random() * 2000
            num4 = random.random() * 2000
            ds["v1"] = (num1, num2, num3, num4) 
            self.runtime.run("atan_ps")
            rez_asm = ds["v1"]
            rez_py1 = math.atan(num1)
            rez_py2 = math.atan(num2)
            rez_py3 = math.atan(num3)
            rez_py4 = math.atan(num4)

            self.assertAlmostEqual(rez_asm[0], rez_py1, 3)
            self.assertAlmostEqual(rez_asm[1], rez_py2, 3)
            self.assertAlmostEqual(rez_asm[2], rez_py3, 3)
            self.assertAlmostEqual(rez_asm[3], rez_py4, 3)

    def test_asin(self):
        mc = self.assembler.assemble(ASIN_CODE)
        ds = self.runtime.load('asin', mc)

        for x in range(1000):
            num = random.random() 
            ds["x"] = num 
            self.runtime.run("asin")
            rez_asm = ds["x"]
            rez_py = math.asin(num)
            self.assertAlmostEqual(rez_asm, rez_py, 3)

    def test_asin_ps(self):
        mc = self.assembler.assemble(ASIN_CODE_PS)
        ds = self.runtime.load('asin_ps', mc)

        for x in range(1000):
            num1 = random.random() 
            num2 = random.random() 
            num3 = random.random() 
            num4 = random.random()
            ds["v1"] = (num1, num2, num3, num4) 
            self.runtime.run("asin_ps")
            rez_asm = ds["v1"]
            rez_py1 = math.asin(num1)
            rez_py2 = math.asin(num2)
            rez_py3 = math.asin(num3)
            rez_py4 = math.asin(num4)

            self.assertAlmostEqual(rez_asm[0], rez_py1, 3)
            self.assertAlmostEqual(rez_asm[1], rez_py2, 3)
            self.assertAlmostEqual(rez_asm[2], rez_py3, 3)
            self.assertAlmostEqual(rez_asm[3], rez_py4, 3)

    def test_acos(self):
        mc = self.assembler.assemble(ACOS_CODE)
        ds = self.runtime.load('acos', mc)

        for x in range(1000):
            num = random.random() 
            ds["x"] = num 
            self.runtime.run("acos")
            rez_asm = ds["x"]
            rez_py = math.acos(num)
            self.assertAlmostEqual(rez_asm, rez_py, 2)

    def test_acos_ps(self):
        mc = self.assembler.assemble(ACOS_CODE_PS)
        ds = self.runtime.load('acos_ps', mc)

        for x in range(1000):
            num1 = random.random() 
            num2 = random.random() 
            num3 = random.random() 
            num4 = random.random()
            ds["v1"] = (num1, num2, num3, num4) 
            self.runtime.run("acos_ps")
            rez_asm = ds["v1"]
            rez_py1 = math.acos(num1)
            rez_py2 = math.acos(num2)
            rez_py3 = math.acos(num3)
            rez_py4 = math.acos(num4)

            self.assertAlmostEqual(rez_asm[0], rez_py1, 2)
            self.assertAlmostEqual(rez_asm[1], rez_py2, 2)
            self.assertAlmostEqual(rez_asm[2], rez_py3, 2)
            self.assertAlmostEqual(rez_asm[3], rez_py4, 2)

    def test_tan(self):
        mc = self.assembler.assemble(TAN_CODE)
        ds = self.runtime.load('tan', mc)

        for x in range(1000):
            num = random.random()  
            ds["x"] = num 
            self.runtime.run("tan")
            rez_asm = ds["x"]
            rez_py = math.tan(num)
            self.assertAlmostEqual(rez_asm, rez_py, 1)

    def test_tan_ps(self):
        mc = self.assembler.assemble(TAN_CODE_PS)
        ds = self.runtime.load('tan_ps', mc)

        for x in range(1000):
            num1 = random.random() 
            num2 = random.random()
            num3 = random.random() 
            num4 = random.random() 
            ds["v1"] = (num1, num2, num3, num4) 
            self.runtime.run("tan_ps")
            rez_asm = ds["v1"]
            rez_py1 = math.tan(num1)
            rez_py2 = math.tan(num2)
            rez_py3 = math.tan(num3)
            rez_py4 = math.tan(num4)

            self.assertAlmostEqual(rez_asm[0], rez_py1, 1)
            self.assertAlmostEqual(rez_asm[1], rez_py2, 1)
            self.assertAlmostEqual(rez_asm[2], rez_py3, 1)
            self.assertAlmostEqual(rez_asm[3], rez_py4, 1)

    def test_log(self):
        mc = self.assembler.assemble(LOG_CODE)
        ds = self.runtime.load('log', mc)

        for x in range(1000):
            num = random.random()  
            ds["x"] = num 
            self.runtime.run("log")
            rez_asm = ds["x"]
            rez_py = math.log(num)
            self.assertAlmostEqual(rez_asm, rez_py, 3)

    def test_log_ps(self):
        mc = self.assembler.assemble(LOG_CODE_PS)
        ds = self.runtime.load('log_ps', mc)

        for x in range(1000):
            num1 = random.random() 
            num2 = random.random()
            num3 = random.random() 
            num4 = random.random() 
            ds["v1"] = (num1, num2, num3, num4) 
            self.runtime.run("log_ps")
            rez_asm = ds["v1"]
            rez_py1 = math.log(num1)
            rez_py2 = math.log(num2)
            rez_py3 = math.log(num3)
            rez_py4 = math.log(num4)

            self.assertAlmostEqual(rez_asm[0], rez_py1, 3)
            self.assertAlmostEqual(rez_asm[1], rez_py2, 3)
            self.assertAlmostEqual(rez_asm[2], rez_py3, 3)
            self.assertAlmostEqual(rez_asm[3], rez_py4, 3)

if __name__ == "__main__":
    unittest.main()


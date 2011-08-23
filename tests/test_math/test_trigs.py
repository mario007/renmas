

import random
import unittest
import math

from renmas.maths import load_math_func 
from tdasm import Tdasm, Runtime

SIN_CODE = """
#DATA
float x
float v1[4]

#CODE
movss xmm0, dword [x]
call fast_sin_ss
movss dword [x], xmm0 

#END
"""


SIN_CODE_PS = """
#DATA
float x
float v1[4]

#CODE
movaps xmm0, oword [v1]
call fast_sin_ps
movaps oword [v1], xmm0 

#END
"""

COS_CODE = """
#DATA
float x
float v1[4]

#CODE
movss xmm0, dword [x]
call fast_cos_ss
movss dword [x], xmm0 

#END
"""

COS_CODE_PS = """
#DATA
float x
float v1[4]

#CODE
movaps xmm0, oword [v1]
call fast_cos_ps
movaps oword [v1], xmm0 

#END
"""

SINCOS_CODE = """
#DATA
float x, y

#CODE
movss xmm0, dword [x]
call fast_sincos_ss
movss dword [x], xmm0 
movss dword [y], xmm6

#END
"""

SINCOS_CODE_PS = """
#DATA
float x
float v1[4]
float v2[4]

#CODE
movaps xmm0, oword [v1]
call fast_sincos_ps
movaps oword [v1], xmm0 
movaps oword [v2], xmm6

#END
"""

EXP_CODE = """
#DATA
float x
float v1[4]

#CODE
movss xmm0, dword [x]
call fast_exp_ss
movss dword [x], xmm0 

#END
"""

EXP_CODE_PS = """
#DATA
float x
float v1[4]

#CODE
movaps xmm0, oword [v1]
call fast_exp_ps
movaps oword [v1], xmm0 

#END
"""

POW_CODE = """
#DATA
float x, y

#CODE
movss xmm0, dword [x]
movss xmm1, dword [y]
call fast_pow_ss
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
call fast_pow_ps
movaps oword [v1], xmm0 

#END
"""
ATAN_CODE = """
#DATA
float x
float v1[4]

#CODE
movss xmm0, dword [x]
call fast_atan_ss
movss dword [x], xmm0 

#END
"""

ATAN_CODE_PS = """
#DATA
float x
float v1[4]

#CODE
movaps xmm0, oword [v1]
call fast_atan_ps
movaps oword [v1], xmm0 

#END
"""

ASIN_CODE = """
#DATA
float x
float v1[4]

#CODE
movss xmm0, dword [x]
call fast_asin_ss
movss dword [x], xmm0 

#END
"""

ASIN_CODE_PS = """
#DATA
float x
float v1[4]

#CODE
movaps xmm0, oword [v1]
call fast_asin_ps
movaps oword [v1], xmm0 

#END
"""

ACOS_CODE = """
#DATA
float x
float v1[4]

#CODE
movss xmm0, dword [x]
call fast_acos_ss
movss dword [x], xmm0 

#END
"""

ACOS_CODE_PS = """
#DATA
float x
float v1[4]

#CODE
movaps xmm0, oword [v1]
call fast_acos_ps
movaps oword [v1], xmm0 

#END
"""

TAN_CODE = """
#DATA
float x
float v1[4]

#CODE
movss xmm0, dword [x]
call fast_tan_ss
movss dword [x], xmm0 

#END
"""

TAN_CODE_PS = """
#DATA
float x
float v1[4]

#CODE
movaps xmm0, oword [v1]
call fast_tan_ps
movaps oword [v1], xmm0 

#END
"""

LOG_CODE = """
#DATA
float x
float v1[4]

#CODE
movss xmm0, dword [x]
call fast_log_ss
movss dword [x], xmm0 

#END
"""

LOG_CODE_PS = """
#DATA
float x
float v1[4]

#CODE
movaps xmm0, oword [v1]
call fast_log_ps
movaps oword [v1], xmm0 

#END
"""

class TestTrigs(unittest.TestCase):

    def setUp(self):
        pass

    def test_sin(self):
        asm = Tdasm()
        mc = asm.assemble(SIN_CODE)
        runtime = Runtime()
        load_math_func("fast_sin_ss", runtime)
        ds = runtime.load("sin", mc)

        for x in range(1000):
            num = random.random() * 2000
            ds["x"] = num 
            runtime.run("sin")
            rez_asm = ds["x"]
            rez_py = math.sin(num)
            self.assertAlmostEqual(rez_asm, rez_py, 3)

    def test_sin_ps(self):
        asm = Tdasm()
        mc = asm.assemble(SIN_CODE_PS)
        runtime = Runtime()
        load_math_func("fast_sin_ps", runtime)
        ds = runtime.load("sin_ps", mc)

        for x in range(1000):
            num1 = random.random() * 2000
            num2 = random.random() * 2000
            num3 = random.random() * 2000
            num4 = random.random() * 2000
            ds["v1"] = (num1, num2, num3, num4) 
            runtime.run("sin_ps")
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
        asm = Tdasm()
        mc = asm.assemble(COS_CODE)
        runtime = Runtime()
        load_math_func("fast_cos_ss", runtime)
        ds = runtime.load("cos", mc)

        for x in range(1000):
            num = random.random() * 2000
            ds["x"] = num 
            runtime.run("cos")
            rez_asm = ds["x"]
            rez_py = math.cos(num)
            self.assertAlmostEqual(rez_asm, rez_py, 3)

    def test_cos_ps(self):
        asm = Tdasm()
        mc = asm.assemble(COS_CODE_PS)
        runtime = Runtime()
        load_math_func("fast_cos_ps", runtime)
        ds = runtime.load("cos_ps", mc)

        for x in range(1000):
            num1 = random.random() * 2000
            num2 = random.random() * 2000
            num3 = random.random() * 2000
            num4 = random.random() * 2000
            ds["v1"] = (num1, num2, num3, num4) 
            runtime.run("cos_ps")
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
        asm = Tdasm()
        mc = asm.assemble(SINCOS_CODE)
        runtime = Runtime()
        load_math_func("fast_sincos_ss", runtime)
        ds = runtime.load("sincos", mc)

        for x in range(1000):
            num = random.random() * 2000
            ds["x"] = num 
            runtime.run("sincos")
            rez_asm1 = ds["x"]
            rez_asm2 = ds["y"]

            rez_py1, rez_py2 = math.sin(num), math.cos(num)
            self.assertAlmostEqual(rez_asm1, rez_py1, 3)
            self.assertAlmostEqual(rez_asm2, rez_py2, 3)

    def test_sincos_ps(self):
        asm = Tdasm()
        mc = asm.assemble(SINCOS_CODE_PS)
        runtime = Runtime()
        load_math_func("fast_sincos_ps", runtime)
        ds = runtime.load("sincos_ps", mc)

        for x in range(1000):
            num1 = random.random() * 2000
            num2 = random.random() * 2000
            num3 = random.random() * 2000
            num4 = random.random() * 2000
            ds["v1"] = (num1, num2, num3, num4) 
            runtime.run("sincos_ps")
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
        asm = Tdasm()
        mc = asm.assemble(EXP_CODE)
        runtime = Runtime()
        load_math_func("fast_exp_ss", runtime)
        ds = runtime.load("exp", mc)

        for x in range(1000):
            num = random.random() * 4 
            ds["x"] = num 
            runtime.run("exp")
            rez_asm = ds["x"]
            rez_py = math.exp(num)
            self.assertAlmostEqual(rez_asm, rez_py, 2)

    def test_exp_ps(self):
        asm = Tdasm()
        mc = asm.assemble(EXP_CODE_PS)
        runtime = Runtime()
        load_math_func("fast_exp_ps", runtime)
        ds = runtime.load("exp_ps", mc)

        for x in range(1000):
            num1 = random.random() * 4 
            num2 = random.random() * 4
            num3 = random.random() * 4
            num4 = random.random() * 4
            ds["v1"] = (num1, num2, num3, num4) 
            runtime.run("exp_ps")
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
        asm = Tdasm()
        mc = asm.assemble(POW_CODE)
        runtime = Runtime()
        load_math_func("fast_pow_ss", runtime)
        ds = runtime.load("pow", mc)

        for x in range(1000):
            num = random.random() * 3 
            num1 = random.random() * 3 
            ds["x"] = num 
            ds["y"] = num1 
            runtime.run("pow")
            rez_asm = ds["x"]
            rez_py = math.pow(num, num1)
            self.assertAlmostEqual(rez_asm, rez_py, 1)

    def test_pow_ps(self):
        asm = Tdasm()
        mc = asm.assemble(POW_CODE_PS)
        runtime = Runtime()
        load_math_func("fast_pow_ps", runtime)
        ds = runtime.load("pow_ps", mc)

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
            runtime.run("pow_ps")
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
        asm = Tdasm()
        mc = asm.assemble(ATAN_CODE)
        runtime = Runtime()
        load_math_func("fast_atan_ss", runtime)
        ds = runtime.load("atan", mc)

        for x in range(1000):
            num = random.random() * 2000
            ds["x"] = num 
            runtime.run("atan")
            rez_asm = ds["x"]
            rez_py = math.atan(num)
            self.assertAlmostEqual(rez_asm, rez_py, 3)

    def test_atan_ps(self):
        asm = Tdasm()
        mc = asm.assemble(ATAN_CODE_PS)
        runtime = Runtime()
        load_math_func("fast_atan_ps", runtime)
        ds = runtime.load("atan_ps", mc)

        for x in range(1000):
            num1 = random.random() * 2000
            num2 = random.random() * 2000
            num3 = random.random() * 2000
            num4 = random.random() * 2000
            ds["v1"] = (num1, num2, num3, num4) 
            runtime.run("atan_ps")
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
        asm = Tdasm()
        mc = asm.assemble(ASIN_CODE)
        runtime = Runtime()
        load_math_func("fast_asin_ss", runtime)
        ds = runtime.load("asin", mc)

        for x in range(1000):
            num = random.random() 
            ds["x"] = num 
            runtime.run("asin")
            rez_asm = ds["x"]
            rez_py = math.asin(num)
            self.assertAlmostEqual(rez_asm, rez_py, 3)

    def test_asin_ps(self):
        asm = Tdasm()
        mc = asm.assemble(ASIN_CODE_PS)
        runtime = Runtime()
        load_math_func("fast_asin_ps", runtime)
        ds = runtime.load("asin_ps", mc)

        for x in range(1000):
            num1 = random.random() 
            num2 = random.random() 
            num3 = random.random() 
            num4 = random.random()
            ds["v1"] = (num1, num2, num3, num4) 
            runtime.run("asin_ps")
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
        asm = Tdasm()
        mc = asm.assemble(ACOS_CODE)
        runtime = Runtime()
        load_math_func("fast_acos_ss", runtime)
        ds = runtime.load("acos", mc)

        for x in range(1000):
            num = random.random() 
            ds["x"] = num 
            runtime.run("acos")
            rez_asm = ds["x"]
            rez_py = math.acos(num)
            self.assertAlmostEqual(rez_asm, rez_py, 2)

    def test_acos_ps(self):
        asm = Tdasm()
        mc = asm.assemble(ACOS_CODE_PS)
        runtime = Runtime()
        load_math_func("fast_acos_ps", runtime)
        ds = runtime.load("acos_ps", mc)

        for x in range(1000):
            num1 = random.random() 
            num2 = random.random() 
            num3 = random.random() 
            num4 = random.random()
            ds["v1"] = (num1, num2, num3, num4) 
            runtime.run("acos_ps")
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
        asm = Tdasm()
        mc = asm.assemble(TAN_CODE)
        runtime = Runtime()
        load_math_func("fast_tan_ss", runtime)
        ds = runtime.load("tan", mc)

        for x in range(1000):
            num = random.random()  
            ds["x"] = num 
            runtime.run("tan")
            rez_asm = ds["x"]
            rez_py = math.tan(num)
            self.assertAlmostEqual(rez_asm, rez_py, 1)

    def test_tan_ps(self):
        asm = Tdasm()
        mc = asm.assemble(TAN_CODE_PS)
        runtime = Runtime()
        load_math_func("fast_tan_ps", runtime)
        ds = runtime.load("tan_ps", mc)

        for x in range(1000):
            num1 = random.random() 
            num2 = random.random()
            num3 = random.random() 
            num4 = random.random() 
            ds["v1"] = (num1, num2, num3, num4) 
            runtime.run("tan_ps")
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
        asm = Tdasm()
        mc = asm.assemble(LOG_CODE)
        runtime = Runtime()
        load_math_func("fast_log_ss", runtime)
        ds = runtime.load("log", mc)

        for x in range(1000):
            num = random.random()  
            ds["x"] = num 
            runtime.run("log")
            rez_asm = ds["x"]
            rez_py = math.log(num)
            self.assertAlmostEqual(rez_asm, rez_py, 3)

    def test_log_ps(self):
        asm = Tdasm()
        mc = asm.assemble(LOG_CODE_PS)
        runtime = Runtime()
        load_math_func("fast_log_ps", runtime)
        ds = runtime.load("log_ps", mc)

        for x in range(1000):
            num1 = random.random() 
            num2 = random.random()
            num3 = random.random() 
            num4 = random.random() 
            ds["v1"] = (num1, num2, num3, num4) 
            runtime.run("log_ps")
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



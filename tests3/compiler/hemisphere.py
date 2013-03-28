
import math
import unittest
from random import random
from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float, Vec3, Vec2, Vec4
from renmas3.base import Vector2, Vector3, Vector4, Struct
from renmas3.base import register_user_type, create_user_type

code = """
ret = sample_hemisphere()

"""
props = {'ret':Vector3(5,6,7)}
bs = BasicShader(code, props)
runtime = Runtime()
bs.prepare([runtime])
print (bs.shader._code)

bs.execute()
val = bs.shader.get_value('ret')
print(val)

def gen_sample():
    r1 = random()
    r2 = random()

    phi = 2.0 * math.pi * r2
    pu = math.sqrt(1.0 - r1) * math.cos(phi)
    pv = math.sqrt(1.0 - r1) * math.sin(phi)
    pw = math.sqrt(r1)
    return pu, pv, pw

print(gen_sample())

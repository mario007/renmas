
import math
import unittest
from random import random
from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float, Vec3, Vec2, Vec4
from renmas3.base import Vector2, Vector3, Vector4, Struct
from renmas3.base import register_user_type, create_user_type

code = """
ret = random()
ret2 = random2()
ret3 = random3()
ret4 = random4()
"""
props = {'ret':1.1, 'ret2':Vector2(2.2, 4), 'ret3':Vector3(5,6,7),
        'ret4':Vector4(11,1,1,1)}
bs = BasicShader(code, props)
runtime = Runtime()
bs.prepare([runtime])
print (bs.shader._code)

bs.execute()
val = bs.shader.get_value('ret')
print(val)
val = bs.shader.get_value('ret2')
print(val)
val = bs.shader.get_value('ret3')
print(val)
val = bs.shader.get_value('ret4')
print(val)

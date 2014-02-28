
import unittest
from tdasm import Runtime
from sdl.vector import Vector2, Vector3, Vector4
from sdl.shader import Shader
from sdl.args import IntArg, FloatArg, Vec2Arg, Vec3Arg, Vec4Arg

code = """
p1 = rand_int()
p2 = random()
p3 = random2()
p4 = random3()
p5 = random4()
"""
p1 = IntArg('p1', 333)
p2 = FloatArg('p2', 333.0)
p3 = Vec2Arg('p3', Vector2(0.0, 0.0))
p4 = Vec3Arg('p4', Vector3(0.0, 0.0, 0.0))
p5 = Vec4Arg('p5', Vector4(0.0, 0.0, 0.0, 0.0))
shader = Shader(code=code, args=[p1, p2, p3, p4, p5])
shader.compile()
shader.prepare([Runtime()])
shader.execute()

print(shader.get_value('p1'))
print(shader.get_value('p2'))
print(shader.get_value('p3'))
print(shader.get_value('p4'))
print(shader.get_value('p5'))

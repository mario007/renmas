
from tdasm import Runtime
from renmas3.base import Vector3, Ray
from renmas3.samplers import Sample
from renmas3.cameras import Camera
from renmas3.base import create_shader, arg_map

eye = Vector3(2.2, 3.3, 4.4)
lookat = Vector3(1.1, 2.2, 0.0)
distance = 3.3
sample = Sample(2.2, 3.3, 5, 6, 1.0)

code = """
tmp1 = u * sample.x
tmp2 = v * sample.y
tmp3 = w * distance
direction = tmp1 + tmp2 - tmp3
ray.origin = eye
ray.direction =  normalize(direction)

"""

def generate_ray(props, sample):
    direction = props['u'] * sample.x + props['v'] * sample.y - props['w'] * props['distance']
    direction.normalize()
    return Ray(props['eye'], direction)

camera = Camera(eye, lookat, distance, code=code, py_code=generate_ray)

runtimes = [Runtime()]
camera.prepare(runtimes)

ray = camera.execute_py(sample)


call_code = """
generate_ray(sample, ray)
"""
args = arg_map([('sample', Sample), ('ray', Ray)])
shader = create_shader('test', call_code, args=args, shaders=[camera.shader])

shader.prepare(runtimes)
shader.set_value('sample', sample)

shader.execute()

print(ray.origin)
print(shader.get_value('ray.origin'))
print('---------------------------')
print(ray.dir)
print(shader.get_value('ray.direction'))

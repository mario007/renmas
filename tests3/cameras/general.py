
from tdasm import Runtime
from renmas3.base import Vector3, Ray
from renmas3.samplers import Sample
from renmas3.cameras import create_perspective_camera
from renmas3.base import create_shader, arg_map

eye = Vector3(2.2, 3.3, 4.4)
lookat = Vector3(1.1, 2.2, 0.0)
distance = 3.3
sample = Sample(2.2, 3.3, 5, 6, 1.0)

camera = create_perspective_camera(eye, lookat, distance)

runtimes = [Runtime()]
camera.prepare(runtimes)

call_code = """
generate_ray(sample, ray)
"""
args = arg_map([('sample', Sample), ('ray', Ray)])
shader = create_shader('test', call_code, args=args, shaders=[camera.shader])

shader.prepare(runtimes)
shader.set_value('sample', sample)

ray = camera.execute_py(sample)
shader.execute()

def cmp_vec3(vec1, vec2):
    if round(vec1.x - vec2.x, 3) != 0:
        raise ValueError("Vectors are different", vec1, vec2)
    if round(vec1.y - vec2.y, 3) != 0:
        raise ValueError("Vectors are different", vec1, vec2)
    if round(vec1.z - vec2.z, 3) != 0:
        raise ValueError("Vectors are different", vec1, vec2)

def compare_rays(ray, shader):
    cmp_vec3(ray.origin, shader.get_value('ray.origin'))
    cmp_vec3(ray.dir, shader.get_value('ray.direction'))


compare_rays(ray, shader)

print(ray.origin)
print(shader.get_value('ray.origin'))
print('---------------------------')
print(ray.dir)
print(shader.get_value('ray.direction'))

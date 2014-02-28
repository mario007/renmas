
from sdl import Vector3, Vec3Arg, Shader,\
    FloatArg, Ray, StructArgPtr

from .hitpoint import HitPoint

def ray_triangle_isect_shader(name, isect_bool=False):
    code = """
origin = ray.origin
direction = ray.direction
a = p0[0] - p1[0]
b = p0[0] - p2[0]
c = direction[0]
d = p0[0] - origin[0]
e = p0[1] - p1[1]
f = p0[1] - p2[1]
g = direction[1]
h = p0[1]- origin[1]
i = p0[2] - p1[2]
j = p0[2] - p2[2]
k = direction[2]
l = p0[2] - origin[2]

m = f * k - g * j
n = h * k - g * l
p = f * l - h * j
q = g * i - e * k
s = e * j - f * i

temp3 =  a * m + b * q + c * s

if temp3 == 0.0:
    return 0
inv_denom = 1.0 / temp3

e1 = d * m - b * n - c * p
beta = e1 * inv_denom

if beta < 0.0:
    return 0

r = e * l - h * i
e2 = a * n + d * q + c * r
gamma = e2 * inv_denom

if gamma < 0.0:
    return 0

betagamma = beta + gamma
if betagamma > 1.0:
    return 0

e3 = a * p - b * r + d * s
t = e3 * inv_denom

epsilon = 0.00001
if t < 0.00001:
    return 0

if t > min_dist:
    return 0
    """
    if isect_bool:
        code += """
return 1
        """
    else:
        code += """
hitpoint.t = t
hitpoint.hit = direction * t + origin 
hitpoint.u = beta
hitpoint.v = gamma
return 1

        """
    origin = Vector3(0.0, 0.0, 0.0)
    direction = Vector3(0.0, 0.0, 0.0)
    ray = Ray(origin, direction)
    ray_a = StructArgPtr('ray', ray)
    p0 = Vec3Arg('p0', Vector3(0.0, 0.0, 0.0))
    p1 = Vec3Arg('p1', Vector3(0.0, 0.0, 0.0))
    p2 = Vec3Arg('p2', Vector3(0.0, 0.0, 0.0))
    dist = FloatArg('min_dist', 0.0)

    hitpoint = HitPoint(0.0, Vector3(0.0, 0.0, 0.0),
                        Vector3(0.0, 0.0, 0.0), 0, 0.0, 0.0)
    hit_a = StructArgPtr('hitpoint', hitpoint)
    if isect_bool:
        func_args = [ray_a, p0, p1, p2, dist]
    else:
        func_args = [ray_a, p0, p1, p2, dist, hit_a]

    shader = Shader(code=code, args=[], name=name,
                    func_args=func_args, is_func=True)
    return shader


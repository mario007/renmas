
from sdl import Vector3, Vec3Arg, Shader,\
    FloatArg, Ray, StructArgPtr, IntArg

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
    ray_a = StructArgPtr('ray', Ray.factory())
    p0 = Vec3Arg('p0', Vector3(0.0, 0.0, 0.0))
    p1 = Vec3Arg('p1', Vector3(0.0, 0.0, 0.0))
    p2 = Vec3Arg('p2', Vector3(0.0, 0.0, 0.0))
    dist = FloatArg('min_dist', 0.0)
    hit_a = StructArgPtr('hitpoint', HitPoint.factory())
    if isect_bool:
        func_args = [ray_a, p0, p1, p2, dist]
    else:
        func_args = [ray_a, p0, p1, p2, dist, hit_a]

    shader = Shader(code=code, args=[], name=name,
                    func_args=func_args, is_func=True)
    return shader


def argument_factory(name, cls):
    if cls == int:
        return IntArg(name, int())
    elif cls == float:
        return FloatArg(name, float())
    elif cls == Vector3:
        return Vec3Arg(name, Vector3.zero())
    else:
        raise ValueError("Argument factory. Unsuported arugment type", name, cls)


def shader(func_args):
    def wrap(func):
        def wrapped_f(*args, **kwargs):
            arguments = []
            for arg in func_args:
                name, cls = arg
                a = argument_factory(name, cls)
                arguments.append(a)
            code = func(*args, **kwargs)
            name = func.__name__
            return Shader(code=code, args=[], name=name,
                          func_args=arguments, is_func=True)
        return wrapped_f
    return wrap


@shader([('normal', Vector3), ('incident', Vector3)])
def reflect():
    return "return incident - 2.0 * dot(normal, incident) * normal"


@shader([('normal', Vector3), ('incident', Vector3),
         ('n1', float), ('n2', float)])
def refract():
    code = """
n = n1 / n2
cosi = dot(normal, incident) * -1.0
sint2 = n * n * (1.0 - cosi * cosi)
if sint2 > 1.0:  # TIR
    return (0.0, 0.0, 0.0)  # invalid vector
tmp = 1.0 - sint2
cost = sqrt(tmp)
return n * incident + (n * cosi - cost) * normal
    """
    return code


@shader([('normal', Vector3), ('incident', Vector3),
         ('n1', float), ('n2', float)])
def dielectric_reflectance():
    code = """
n = n1 / n2
cosi = dot(normal, incident) * -1.0
sint2 = n * n * (1.0 - cosi * cosi)
if sint2 > 1.0:  # TIR
    return 1.0
tmp = 1.0 - sint2
cost = sqrt(tmp)
rorth = (n1 * cosi - n2 * cost) / (n1 * cosi + n2 * cost)
rpar = (n2 * cosi - n1 * cost) / (n2 * cosi + n1 * cost)
return (rorth * rorth + rpar * rpar) * 0.5
    """
    return code


@shader([('normal', Vector3), ('incident', Vector3),
         ('n1', float), ('n2', float)])
def tmp_dielectric_reflectance():
    code = """
tmp = normal * -1.0
ndotd = dot(tmp, incident) 
if ndotd < 0.0:
    normal = normal * -1.0
    eta = n1 / n2
else:
    eta = n2 / n1

tmp = normal * -1.0
cos_theta_i =  dot(tmp, incident)

tmp = 1.0 - (1.0 - cos_theta_i * cos_theta_i) / (eta * eta)
cos_theta_t = sqrt(tmp)

rpara = (eta * cos_theta_i - cos_theta_t) / (eta * cos_theta_i + cos_theta_t)
ropr = (cos_theta_i - eta * cos_theta_t) / (cos_theta_i + eta * cos_theta_t)

kr = 0.5 * (rpara * rpara + ropr * ropr)
return kr
    """
    return code


@shader([('normal', Vector3), ('incident', Vector3),
         ('n1', float), ('n2', float)])
def tir():
    code = """
n = n1 / n2
cosi = dot(normal, incident) * -1.0
sint2 = n * n * (1.0 - cosi * cosi)
if sint2 > 1.0:  # TIR
    return 1
return 0
    """
    return code


def shaders_functions():
    s1 = reflect()
    s2 = refract()
    s3 = dielectric_reflectance()
    s4 = tir()
    return [s1, s2, s3, s4]

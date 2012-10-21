
from random import random
from tdasm import Tdasm, Runtime
from renmas3.core import Factory, ColorManager, Ray, ShadePoint
from renmas3.shapes import Sphere
from renmas3.shapes import  ray_triangle_intersection
from renmas3.core import Vector3

def ray_triangle_isect(v0, v1, v2, origin, direction): #ray direction must be normalized
        
        a = v0.x - v1.x
        b = v0.x - v2.x
        c = direction.x 
        d = v0.x - origin.x
        e = v0.y - v1.y
        f = v0.y - v2.y
        g = direction.y
        h = v0.y - origin.y
        i = v0.z - v1.z
        j = v0.z - v2.z
        k = direction.z
        l = v0.z - origin.z

        m = f * k - g * j
        n = h * k - g * l
        p = f * l - h * j
        q = g * i - e * k
        s = e * j - f * i

        temp3 =  (a * m + b * q + c * s)

        if temp3 == 0.0: return False
        inv_denom = 1.0 / temp3

        e1 = d * m - b * n - c * p
        beta = e1 * inv_denom

        if beta < 0.0: return False

        r = e * l - h * i
        e2 = a * n + d * q + c * r
        gamma = e2 * inv_denom

        if gamma < 0.0: return False

        if beta + gamma > 1.0: return False

        e3 = a * p - b * r + d * s
        t = e3 * inv_denom

        if t < 0.00001: return False # self-intersection

        return (beta, gamma, t)

        
code = ray_triangle_intersection("ray_triangle_intersection")

asm = Tdasm()
mc = asm.assemble(code, True)

runtime = Runtime()
runtime.load('ray_triangle', mc)

# xmm3 - origin
# xmm4 - direction
# xmm5 - p0
# xmm6 - p1
# xmm7 - p2
# edx - min_distance

test_code = """
#DATA
float p0[4]
float p1[4]
float p2[4]
float origin[4]
float direction[4]
float d
float td
float gamma
float beta
float min_dist = 99999.444
int32 ret

#CODE
movaps xmm3, oword [origin]
movaps xmm4, oword [direction]
movaps xmm5, oword [p0]
movaps xmm6, oword [p1]
movaps xmm7, oword [p2]
mov edx, dword [min_dist]
call ray_triangle_intersection
movss dword [td], xmm0
movss dword [gamma], xmm2
movss dword [beta], xmm1
mov dword [ret], eax

; xmm7 = d  xmm6 = td  xmm5 = gamma   xmm4 = beta
#END
"""
mc2 = asm.assemble(test_code)
ds = runtime.load('test', mc2)

def gen_vectors():
    v0 = Vector3(random()*3, random()*3, random()*3)
    v1 = Vector3(random()*3, random()*3, random()*3)
    v2 = Vector3(random(), random(), random())
    origin = Vector3(0, 0, 0)
    direction = Vector3(random(), random(), random())
    direction.normalize()

    return (v0, v1, v2, origin, direction)

for x in range(100):
    v0, v1, v2, origin, direction = gen_vectors()

    ds['p0'] = v0.to_ds()
    ds['p1'] = v1.to_ds()
    ds['p2'] = v2.to_ds()
    ds['origin'] = origin.to_ds()
    ds['direction'] = direction.to_ds()

    runtime.run('test')
    ret = ray_triangle_isect(v0, v1, v2, origin, direction)

    if ret is False and ds['ret'] == 1:
        print(ds['beta'], ds['gamma'], ds['t'])
        raise ValueError("Exception if intersection")
    if ret is not False and ds['ret'] == 0:
        beta, gamma, t = ret 
        print(ds['beta'], ds['gamma'], ds['td'])
        print(beta, gamma, t)
        raise ValueError("Exception if intersection")

    if ret is not False:
        beta, gamma, t = ret 
        print(ds['beta'], ds['gamma'], ds['td'])
        print(beta, gamma, t)
        print('------------------------------------')


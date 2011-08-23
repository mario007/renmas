
from tdasm import Tdasm, Runtime
from renmas.maths import Vector3
from renmas.shapes import Triangle, intersect_ray_shape_array
from renmas.core import Ray
import random
import renmas.utils as util
import timeit

asm_structs = util.structs("ray", "triangle", "hitpoint")

SSE2_ASM = """
    #DATA
"""
SSE2_ASM += asm_structs + """
    ray r1
    triangle tri1 
    hitpoint hp
    float one = 1.0
    float zero = 0.0
    float epsilon = 0.00001
    float beta
    float coff 
    float min_dist = 999999.0

    float xm0[4]
    float xm1[4]
    float xm2[4]
    float xm3[4]
    float xm4[4]
    float xm5[4]
    float xm6[4]
    float xm7[4]
    uint32 xm0i[4]
    uint32 result

    uint32 n = 1000000

    #CODE
    mov eax, r1
    mov ebx, tri1
    mov ecx, min_dist
    mov edx, hp
    call ray_triangle
    movaps oword [xm0], xmm0
    movaps oword [xm1], xmm1
    movaps oword [xm2], xmm2
    movaps oword [xm3], xmm3
    movaps oword [xm4], xmm4
    movaps oword [xm5], xmm5
    movaps oword [xm6], xmm6
    movaps oword [xm7], xmm7
    movaps oword [xm0i], xmm0
    mov dword [result], eax

    #END

    global ray_triangle:
    movaps xmm0, oword [ebx + triangle.p0]
    movaps xmm2, oword [eax + ray.dir]
    movaps xmm1, xmm0
    subps xmm1, oword [ebx + triangle.p2]
    movaps xmm3, xmm0
    subps xmm3, oword [eax + ray.origin]
    subps xmm0, oword [ebx + triangle.p1]

    
    ; f f h f
    movaps xmm4, xmm1
    movlhps xmm4, xmm3
    shufps xmm4, xmm4, 01110101B

    ; k k k l
    movaps xmm5, xmm2
    movhlps xmm5, xmm3
    shufps xmm5, xmm5, 00101010B 

    ; f f h f * k k k l
    movaps xmm7, xmm4
    mulps xmm7, xmm5

    ; g g g h
    movaps xmm6, xmm2
    movlhps xmm6, xmm3
    shufps xmm6, xmm6, 11010101B

    ; j j l j
    movaps xmm4, xmm1
    movhlps xmm4, xmm3
    shufps xmm4, xmm4, 10001010B

    ; g g g h * j j l j
    mulps xmm4, xmm6

    ; f f h f * k k k l - g g g h * j j l j
    subps xmm7, xmm4

    ; a d a a
    movaps xmm5, xmm0
    movlhps xmm5, xmm3
    shufps xmm5, xmm5, 00001000B

    ; a d a a * (f f h f * k k k l - g g g h * j j l j)
    mulps xmm7, xmm5

    ; i l i i
    movaps xmm5, xmm0
    movhlps xmm5, xmm3
    shufps xmm5, xmm5, 10100010B

    ; g g g h * i l i i
    mulps xmm6, xmm5

    ; e h e e
    movaps xmm4, xmm0
    movlhps xmm4, xmm3
    shufps xmm4, xmm4, 01011101B

    ; k k k l
    movaps xmm5, xmm2
    movhlps xmm5, xmm3
    shufps xmm5, xmm5, 00101010B 

    ; e h e e * k k k l
    mulps xmm5, xmm4

    ; g g g h * i l i i - e h e e * k k k l
    subps xmm6, xmm5

    ; b b d b
    movaps xmm5, xmm1
    movlhps xmm5, xmm3
    shufps xmm5, xmm5, 00100000B

    ; b b d b * (g g g h * i l i i - e h e e * k k k l)
    mulps xmm6, xmm5

    addps xmm7, xmm6

    ; j j l j
    movaps xmm5, xmm1
    movhlps xmm5, xmm3
    shufps xmm5, xmm5, 10001010B

    ; e e h e * j j l j 
    mulps xmm4, xmm5

    ; f f h f
    movaps xmm6, xmm1
    movlhps xmm6, xmm3
    shufps xmm6, xmm6, 01110101B

    ; i l i i
    movaps xmm5, xmm0
    movhlps xmm5, xmm3
    shufps xmm5, xmm5, 10100010B

    ; f f h f * i l i i
    mulps xmm6, xmm5

    ; e h e e * j j l j - f f h f * i l i i
    subps xmm4, xmm6

    ; c c c d
    movaps xmm5, xmm2
    movlhps xmm5, xmm3
    shufps xmm5, xmm5, 10000000B

    ; c c c d * (e h e e * j j l j - f f h f * i l i i)
    mulps xmm4, xmm5

    addps xmm7, xmm4

    movhlps xmm5, xmm7
    
    movaps xmm4, xmm7
    shufps xmm4, xmm4, 0x55 
    
    movaps xmm6, xmm7
    shufps xmm6, xmm6, 0xFF

    ; xmm7 = d
    ; xmm6 = td
    ; xmm5 = gamma
    ; xmm4 = beta

    pxor xmm3, xmm3

    ; beta < 0.0
    movaps xmm0, xmm7
    xorps xmm0, xmm4
    cmpss xmm0, xmm3, 5

    ; gamma < 0.0
    movaps xmm1, xmm7
    xorps xmm1, xmm5 
    cmpss xmm1, xmm3, 5

    ; accumulation of conditions
    andps xmm0, xmm1

    ; beta + gamma < 1.0
    movaps xmm2, xmm4
    addps xmm2, xmm5
    cmpss xmm2, xmm6, 2

    andps xmm0, xmm2
    movd esi, xmm0
    cmp esi, 0 
    jne _accept
    xor eax, eax
    ret

    _accept:
    divss xmm6, xmm7

    comiss xmm6, dword [epsilon]
    jc _reject
    comiss xmm6, dword [ecx] ;minimum distance
    jnc _reject

    ;populate hitpoint structure
    ; t is in xmm6
    
    movaps xmm2, oword [eax + ray.dir]
    movaps xmm3, oword [ebx + triangle.normal]
    movss xmm4, dword [ebx + triangle.mat_index]
    

    movss dword [edx + hitpoint.t], xmm6 
    movaps oword [edx + hitpoint.normal], xmm3
    movss dword [edx + hitpoint.mat_index], xmm4
    macro broadcast xmm5 = xmm6[0]
    mulps xmm5, xmm2

    macro eq128 edx.hitpoint.hit = xmm5 + eax.ray.origin

    mov eax, 1
    ret

    _reject:
    xor eax, eax
    ret


"""

def create_triangle():
    p0 = Vector3(0.1, 0.0, -2.0)    
    p1 = Vector3(4.0, 0.5, 0.2)
    p2 = Vector3(2.2, 4.3, -1.0)
    
    tr = Triangle(p0, p1, p2, 3)
    return tr

def create_ray():
    origin = Vector3(0.0, 0.0, 0.0) 
    dirx = 0.985906665972
    diry = 0.165777376892
    dirz = 0.0224923832256

    #direction = Vector3(8.8, 8.9, 8.7)
    direction = Vector3(dirx, diry, dirz)
    #direction.normalize()
    ray = Ray(origin, direction)
    return ray

def v4(v3):
    return (v3.x, v3.y, v3.z, 0.0)

if __name__ == "__main__":

    tr = create_triangle()
    ray = create_ray() 
    hp = tr.isect(ray)
    if hp is not False:
        print(hp.t)

    asm = util.get_asm()
    mc = asm.assemble(SSE2_ASM)
    #mc.print_machine_code()
    runtime = Runtime()
    ds = runtime.load("test", mc)

    ds["tri1.p0"] = v4(tr.v0)
    ds["tri1.p1"] = v4(tr.v1)
    ds["tri1.p2"] = v4(tr.v2)
    ds["tri1.normal"] = v4(tr.normal)
    ds["tri1.mat_index"] = tr.material

    ds["r1.origin"] = v4(ray.origin)
    ds["r1.dir"] = v4(ray.dir)

    runtime.run("test")
    print("xmm0 = ", ds["xm0"])
    print("xmm1 = ", ds["xm1"])
    print("xmm2 = ", ds["xm2"])
    print("xmm3 = ", ds["xm3"])
    print("xmm4 = ", ds["xm4"])
    print("xmm5 = ", ds["xm5"])
    print("xmm6 = ", ds["xm6"])
    print("xmm7 = ", ds["xm7"])
    print("xmm7i = ", ds["xm0i"])
    print("Rezultat je = ", ds["result"])

    print(ds["hp.normal"])
    print(hp.normal)
    print(ds["hp.mat_index"])
    print(hp.material)
    print(ds["hp.hit"])
    print(hp.hit_point)
    print(ds["hp.t"])
    print(hp.t)


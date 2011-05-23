from tdasm import Tdasm, Runtime
from renmas.maths import Vector3
from renmas.shapes import Triangle, intersect_ray_shape_array
from renmas.core import Ray
import random
import renmas.utils as util
import timeit

asm_structs = util.structs("ray", "triangle", "hitpoint")

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

def create_triangle_array(n):
    lst_arr = []

    dy = util.DynamicArray(Triangle.struct())
    for x in range(n):
        p0 = Vector3(random.random()*10.0-5.0, random.random()*10-5.0, random.random()*10-5.0)    
        p1 = Vector3(random.random()*10.0-5.0, random.random()*10-5.0, random.random()*10-5.0)    
        p2 = Vector3(random.random()*10.0-5.0, random.random()*10-5.0, random.random()*10-5.0)    

        tr = Triangle(p0, p1, p2, 4)
        lst_arr.append(tr)

    dy = util.DynamicArray(Triangle.struct(), len(lst_arr))
    for sh in lst_arr:
        dy.add_instance(sh.struct_params())

    return dy, lst_arr


ASM = """
    #DATA
"""
ASM += asm_structs + """
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

    uint32 n = 1000000

    #CODE
    _loop:
    mov eax, r1
    mov ebx, tri1
    mov ecx, min_dist
    mov edx, hp
    call ray_triangle
    sub dword [n], 1
    jnz _loop

    #END

    global ray_triangle:
    ;vmovaps xmm0, oword [ebx + triangle.p0]
    vmovntdqa xmm0, oword [ebx + triangle.p0]

    ;vmovaps xmm2, oword [eax + ray.dir]
    vmovntdqa xmm2, oword [eax + ray.dir]

    vmovntdqa xmm4, oword [ebx + triangle.p2]
    vsubps xmm1, xmm0, xmm4
    ;vsubps xmm1, xmm0, oword [ebx + triangle.p2]

    vmovntdqa xmm5, oword [eax + ray.origin]
    vsubps xmm3, xmm0, xmm5
    ;vsubps xmm3, xmm0, oword [eax + ray.origin]

    vmovntdqa xmm6, oword [ebx + triangle.p1]
    vsubps xmm0, xmm0, xmm6
    ;vsubps xmm0, xmm0, oword [ebx + triangle.p1]

    vpermilps xmm0, xmm0, 11010010B ;rotate by 1
    vpermilps xmm2, xmm2, 11001001B ; rotate by 2
    
    vblendps xmm4, xmm0, xmm1, 0010b
    vblendps xmm4, xmm4, xmm2, 1
   
    vblendps xmm5, xmm0, xmm1, 0100b
    vblendps xmm5, xmm5, xmm2, 0010b

    vpermilps xmm6, xmm4, 11010010B
    vpermilps xmm7, xmm5, 11001001B

    vmulps xmm4, xmm4, xmm5
    vmulps xmm6, xmm6, xmm7
    vblendps xmm5, xmm0, xmm1, 0001B
    vblendps xmm5, xmm5, xmm2, 0100B
    vsubps xmm4, xmm4, xmm6
    vdpps xmm7, xmm4, xmm5, 0xf1

    vpermilps xmm3, xmm3, 11010010B ;rotate by 1
    vblendps xmm4, xmm1, xmm2, 0001B
    vmovss xmm6, dword [one]
    vblendps xmm4, xmm4, xmm3, 0100B
    vblendps xmm5, xmm1, xmm2, 0010B
    vdivss xmm6, xmm6, xmm7

    vblendps xmm5, xmm5, xmm3, 0001B

    vpermilps xmm7, xmm5, 11001001B
    vmovss dword [coff], xmm6
    vpermilps xmm6, xmm4, 11010010B

    vmulps xmm4, xmm4, xmm5
    vmulps xmm6, xmm6, xmm7

    vblendps xmm5, xmm1, xmm2, 0100B
    vblendps xmm5, xmm5, xmm3, 0010B

    vsubps xmm4, xmm4, xmm6
    vdpps xmm7, xmm4, xmm5, 0xf1

    vmulss xmm7, xmm7, dword [coff]
    vcomiss xmm7, dword [zero]
    jc _reject ;beta less then zero reject 
    vmovss dword [beta], xmm7
    
    vpermilps xmm3, xmm3, 11001001B ; rotate by 2

    vblendps xmm4, xmm0, xmm2, 0001B
    vblendps xmm4, xmm4, xmm3, 0010B
    vpermilps xmm6, xmm4, 11010010B
    vblendps xmm5, xmm0, xmm2, 0010B
    vblendps xmm5, xmm5, xmm3, 0100B
    vpermilps xmm7, xmm5, 11001001B
    vmulps xmm4, xmm4, xmm5
    vmulps xmm6, xmm6, xmm7
    vblendps xmm5, xmm0, xmm2, 0100B
    vblendps xmm5, xmm5, xmm3, 0001B
    vsubps xmm4, xmm4, xmm6
    vdpps xmm7, xmm4, xmm5, 0xf1

    vmulss xmm7, xmm7, dword [coff]
    vcomiss xmm7, dword [zero]
    jc _reject ;beta less then zero reject 
    vaddss xmm7, xmm7, dword [beta]
    vcomiss xmm7, dword [one]
    jnc _reject

    vpermilps xmm3, xmm3, 11001001B ; rotate by 2

    vblendps xmm4, xmm0, xmm1, 0010B
    vblendps xmm4, xmm4, xmm3, 0001B
    vpermilps xmm6, xmm4, 11010010B
    vblendps xmm5, xmm0, xmm1, 0100B
    vblendps xmm5, xmm5, xmm3, 0010B
    vpermilps xmm7, xmm5, 11001001B
    vmulps xmm4, xmm4, xmm5
    vmulps xmm6, xmm6, xmm7
    vblendps xmm5, xmm0, xmm1, 0001B
    vblendps xmm5, xmm5, xmm3, 0100B
    vsubps xmm4, xmm4, xmm6
    vdpps xmm7, xmm4, xmm5, 0xf1
    vmulss xmm7, xmm7, dword [coff]
    vcomiss xmm7, dword [epsilon]
    jc _reject
    vcomiss xmm7, dword [ecx] ;minimum distance
    jnc _reject


    ;populate hitpoint structure
    ; t is in xmm7
    vmovss dword [edx + hitpoint.t], xmm7 
    macro broadcast xmm6 = xmm7[0]
    macro eq128_32 edx.hitpoint.normal = ebx.triangle.normal, edx.hitpoint.mat_index = ebx.triangle.mat_index
    vpermilps xmm2, xmm2, 11001001B ; rotate by 2
    vmulps xmm6, xmm6, xmm2
    macro eq128 edx.hitpoint.hit = xmm6 + eax.ray.origin

    mov eax, 1
    ret

    _reject:
    ;mov eax, 0
    xor eax, eax
    ret
"""

ASM2 = """
#DATA
"""
ASM2 += asm_structs + """

    ray r1
    hitpoint hp
    float min_dist = 999999.0

    uint32 ptr_triangles
    uint32 ntriangles

    #CODE
    mov eax, r1
    mov ebx, hp
    mov ecx, min_dist
    mov esi, dword [ptr_triangles]
    mov edi, dword [ntriangles]
    ; eax - ray, ebx - hp , ecx - min_dist, esi - ptr_spheres, edi - nspheres

    call triangle_array 

"""

ASM3 = """
#DATA
"""
ASM3 += asm_structs + """
    ray r1
    triangle tri1 
    hitpoint hp
    float min_dist = 999999.0
    float epsilon = 0.0001
    float neg_epsilon = -0.0001
    float one = 1.0
    float zero = 0.0
    uint32 mask_abs[4] = 0x7FFFFFFF, 0, 0, 0
    float minus_one = -1.0

    float xm0[4]
    float xm1[4]
    float xm2[4]
    float xm3[4]
    float xm4[4]
    float xm5[4]
    float xm6[4]
    float xm7[4]

    #CODE
    mov eax, r1
    mov ebx, tri1
    mov ecx, min_dist
    mov edx, hp
    call ray_triangle
    #END

    global ray_triangle:
    macro eq128_128 xmm0 = ebx.triangle.p1 - ebx.triangle.p0, xmm1 = ebx.triangle.p2 - ebx.triangle.p0 
    ; e1 = xmm0 , e2 = xmm1
    macro eq128_128 xmm2 = eax.ray.dir, xmm3 = xmm1 {xmm0, xmm1}

    ; p = d x e2
    macro eq128_128 xmm4 = xmm2, xmm5 = xmm3 {xmm0, xmm1}
"""
if util.AVX:
    ASM3 += """
        vshufps xmm2, xmm2, xmm2, 0xC9
        vshufps xmm3, xmm3, xmm3, 0xD2
        macro eq128 xmm2 = xmm2 * xmm3 {xmm0, xmm1}
        vshufps xmm4, xmm4, xmm4, 0xD2
        vshufps xmm5, xmm5, xmm5, 0xC9
    """
else:
    ASM3 += """
        shufps xmm2, xmm2, 0xC9
        shufps xmm3, xmm3, 0xD2
        macro eq128 xmm2 = xmm2 * xmm3 {xmm0, xmm1}
        shufps xmm4, xmm4, 0xD2
        shufps xmm5, xmm5, 0xC9
    """
ASM3 += """
    macro eq128 xmm4 = xmm4 * xmm5 {xmm0, xmm1, xmm2}
    macro eq128 xmm2 = xmm2 - xmm4 {xmm0, xmm1}

    macro dot xmm3 = xmm0 * xmm2 {xmm0, xmm1}
"""
if util.AVX:
    ASM3 += "vpabsd xmm4, xmm3 \n"
else:
    ASM3 += "movaps xmm4, oword [mask_abs] \n"
    ASM3 += "andps xmm4, xmm3 \n"

ASM3 += """

    macro if xmm4 < epsilon goto reject
    macro eq32 xmm4 = one / xmm3 {xmm0, xmm1, xmm2, xmm3}

    ; f = xmm4
    macro eq128 xmm5 = eax.ray.origin - ebx.triangle.p0 {xmm0, xmm1, xmm2, xmm3, xmm4}
    ; s = xmm5

    macro dot xmm2 = xmm2 * xmm5 {xmm0, xmm1, xmm3, xmm4}
    ;s * p(s dot p) = xmm2
    macro eq32 xmm6 = xmm4 * xmm2 {xmm0, xmm1, xmm2, xmm3, xmm4, xmm5}

    macro if xmm6 < zero goto reject
    macro if xmm6 > one goto reject

    ; q = s x e1 
    macro eq128_128 xmm3 = xmm5, xmm7 = xmm0 
"""
if util.AVX:
    ASM3 += """
        vshufps xmm5, xmm5, xmm5, 0xC9
        vshufps xmm0, xmm0, xmm0, 0xD2
        macro eq128 xmm0 = xmm0 * xmm5 

        vshufps xmm3, xmm3, xmm3, 0xD2
        vshufps xmm7, xmm7, xmm7, 0xC9
    """
else:
    ASM3 += """
        shufps xmm5, xmm5, 0xC9
        shufps xmm0, xmm0, 0xD2
        macro eq128 xmm0 = xmm0 * xmm5 

        shufps xmm3, xmm3, 0xD2
        shufps xmm7, xmm7, 0xC9
    """

ASM3 += """
    macro eq128 xmm3 = xmm3 * xmm7 
    macro eq128 xmm0 = xmm0 - xmm3

    macro dot xmm7 = xmm0 * eax.ray.dir {xmm1}
    macro eq32 xmm7 = xmm7 * xmm4

    macro if xmm7 < zero goto reject
    macro eq32 xmm7 = xmm7 + xmm6
    macro if xmm7 > one goto reject

    macro dot xmm6 = xmm1 * xmm0
    macro eq32 xmm6 = xmm6 * xmm4

    ;populate hitpoint structure
    ; t is in xmm6 , t can be negative so we eleminate those
    macro if xmm6 < zero goto reject
    macro if xmm6 > ecx goto reject
    macro eq32 edx.hitpoint.t = xmm6
    macro broadcast xmm7 = xmm6[0]
    macro eq128_32 edx.hitpoint.normal = ebx.triangle.normal, edx.hitpoint.mat_index = ebx.triangle.mat_index
    macro eq128 xmm5 = xmm7 * eax.ray.dir
    macro eq128 edx.hitpoint.hit = xmm5 + eax.ray.origin

    mov eax, 1
    ret

    reject:
    mov eax, 0 
    ret


"""

def isect(ray, shapes):
    min_dist = 999999.0
    hit_point = None
    for s in shapes:
        hit = s.intersect(ray, min_dist)
        if hit is False: continue
        if hit.t < min_dist:
            min_dist = hit.t
            hit_point = hit
    return hit_point


def isect_ray(tr, ray):
    e1 = tr.v1 - tr.v0
    e2 = tr.v2 - tr.v0
    p = ray.dir.cross(e2)
    a = e1.dot(p)

    f = 1 / a

    s = ray.origin - tr.v0

    u = f * s.dot(p)

    q = s.cross(e1)
    v = f * q.dot(ray.dir)

    t = f * e2.dot(q)

    #print("e1", e1)
    #print("e2", e2)
    #print("p", p)
    #print("a", a)
    #print("f", f)
    #print("s", s)
    #print("u", u)
    #print("v", v)
    print("t", t)


if __name__ == "__main__":

    tr = create_triangle()
    ray = create_ray() 
    hp = tr.intersect(ray)
    if hp is not False:
        print(hp.t)

    asm = util.get_asm()
    #mc = asm.assemble(ASM)
    print (ASM3)
    mc = asm.assemble(ASM3)
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

    intersect_ray_shape_array("triangle", runtime, "triangle_array", "ray_triangle")

    #runtime.run("test")
   
    dy_arr, lst_arr = create_triangle_array(100000)
    isect_ray(lst_arr[0], ray)

    hp = isect(ray, lst_arr)
    if hp is not False and hp is not None:
        print("Tocka presjeka", hp.t)

    mc2 = asm.assemble(ASM2)
    ds2 = runtime.load("test2", mc2)

    ds2["r1.origin"] = v4(ray.origin)
    ds2["r1.dir"] = v4(ray.dir)
    ds2["ptr_triangles"] = dy_arr.get_addr()
    ds2["ntriangles"] = dy_arr.size

    #runtime.run("test2")
    t = timeit.Timer(lambda : runtime.run("test2"))
    print ("time", t.timeit(1))
    print("min_dist", ds2["min_dist"], ds2["hp.t"])
    print(ds2["hp.mat_index"])



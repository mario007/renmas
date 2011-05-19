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
    vmovaps xmm0, oword [ebx + triangle.p0]
    vmovaps xmm2, oword [eax + ray.dir]
    vsubps xmm1, xmm0, oword [ebx + triangle.p2]
    vsubps xmm3, xmm0, oword [eax + ray.origin]
    vsubps xmm0, xmm0, oword [ebx + triangle.p1]

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
    movss dword [edx + hitpoint.t], xmm7 
    macro broadcast xmm6 = xmm7[0]
    macro eq128_32 edx.hitpoint.normal = ebx.triangle.normal, edx.hitpoint.mat_index = ebx.triangle.mat_index
    vpermilps xmm2, xmm2, 11001001B ; rotate by 2
    vmulps xmm6, xmm6, xmm2
    macro eq128 edx.hitpoint.hit = xmm6 + eax.ray.origin

    mov eax, 1
    ret

    _reject:
    mov eax, 0
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

if __name__ == "__main__":

    tr = create_triangle()
    ray = create_ray() 
    hp = tr.intersect(ray)
    if hp is not False:
        print(hp.t)

    asm = util.get_asm()
    mc = asm.assemble(ASM)
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
   
    dy_arr, lst_arr = create_triangle_array(10000)
    hp = isect(ray, lst_arr)
    if hp is not False:
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

    print(ds["xm0"])
    print(ds["xm1"])
    print(ds["xm2"])
    print(ds["xm3"])
    print("4=", ds["xm4"])
    print(ds["xm5"])
    print(ds["xm6"])
    print(ds["xm7"])

    print(ds["hp.t"])


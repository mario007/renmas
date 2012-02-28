import time
import unittest
from random import random
import x86
from tdasm import Runtime
import renmas2

class FlatMeshIsectTest(unittest.TestCase):
    def setUp(self):
        self.counter = 0

    def random_ray(self):
        factory = renmas2.Factory()
        #origin = (random(), random(), random())
        origin = (0.0, 0.0, 0.0)
        direction = (random(), random(), random())
        return factory.create_ray(origin, direction)

    def create_triangle_list(self, vb, tb):
        lst_triangles = []
        factory = renmas2.Factory()
        for i in range(tb.size()):
            v0, v1, v2 = tb.get(i)
            p0 = vb.get(v0)
            p1 = vb.get(v1)
            p2 = vb.get(v2)
            triangle = factory.create_triangle(v0=p0, v1=p1, v2=p2)
            lst_triangles.append(triangle)
        return lst_triangles

    def isect_triangles(self, shapes, ray, min_dist=999999.0):
        hit_point = False 
        for s in shapes:
            hit = s.isect(ray, min_dist)
            if hit is False: continue
            if hit.t < min_dist:
                min_dist = hit.t
                hit_point = hit
        return hit_point

    def intersection_tests(self, n, triangles, mesh):

        for i in range(n):
            ray = self.random_ray()
            hp1 = self.isect_triangles(triangles, ray)
            hp2 = mesh.isect(ray)

            if hp1 is None and hp2 is not None:
                print(ray)
                raise ValueError("Intersection failed")
            if hp1 is not None and hp2 is None:
                print(ray)
                raise ValueError("Intersection failed")
            if hp1:
                self.assertAlmostEqual(hp1.t, hp2.t, 4)

    def speed_test(self, n, triangles, mesh):
        for i in range(n):
            ray = self.random_ray()
            #hp = self.isect_triangles(triangles, ray)
            hp = mesh.isect(ray)
            if hp:
                print(hp.t)

    def ray_ds(self, ds, ray, name):
        o = ray.origin
        d = ray.dir
        ds[name+ ".origin"] = (o.x, o.y, o.z, 0.0)
        ds[name+ ".dir"] = (d.x, d.y, d.z, 0.0)

    def flat_mesh_ds(self, ds, mesh, name):
        ds[name + ".vertex_buffer_ptr"] = mesh._vb.addr()
        ds[name + ".vertex_size"] = mesh._vb.item_size()
        ds[name + ".triangle_buffer_ptr"] = mesh._tb.addr()
        ds[name + ".triangle_size"] = mesh._tb.item_size()

    # eax = pointer to ray structure
    # ebx = pointer to flat mesh structure
    # ecx = pointer to minimum distance
    # edx = address in linear grid array --- n:idx1, idx2, ... 
    def asm_code1(self, ren):
        code = """
            #DATA
        """
        code += ren.structures.structs(('ray', 'flat_mesh')) + """
            ray ray1
            flat_mesh mesh1
            float min_dist = 99999.000
            uint32 ret
            uint32 ptr_triangles_arr
            float t
            float hit[4]
            float normal[4]

            #CODE
            mov eax, ray1
            mov ebx, mesh1
            mov ecx, min_dist
            mov edx, dword [ptr_triangles_arr]
            call ray_triangles_idx
            mov dword [ret], eax
            macro eq32 t = xmm0 {xmm7}
            macro eq128 hit = xmm1 {xmm7}
            macro eq128 normal = xmm2 {xmm7}
            

            #END
        """
        return code

    # eax = pointer to ray structure
    # ebx = pointer to flat mesh structure
    # ecx = pointer to minimum distance
    # edx = pointer to hitpoint 
    def asm_code2(self, ren):
        code = """
            #DATA
        """
        code += ren.structures.structs(('ray', 'flat_mesh', 'hitpoint')) + """
            ray ray1
            flat_mesh mesh1
            hitpoint hp1
            float min_dist = 99999.000
            uint32 ret
            float t
            float hit[4]
            float normal[4]

            #CODE
            mov eax, ray1
            mov ebx, mesh1
            mov ecx, min_dist
            mov edx, hp1
            call ray_flat_mash_intersection
            mov dword [ret], eax

            macro eq32 t = xmm0 {xmm7}
            macro eq128 hit = xmm1 {xmm7}
            macro eq128 normal = xmm2 {xmm7}

            #END
        """

    def test_isect1(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()

        ply = renmas2.core.Ply()
        ply.load("I:/Ply_files/cube.ply")
        #ply.load("I:/Ply_files/dragon_vrip.ply")
        #ply.load("I:/Ply_files/xyzrgb_dragon.ply")
        #ply.load("I:/Ply_files/lucy.ply")
        vb = ply._vertex_buffer
        tb = ply._triangle_buffer
        mesh = factory.create_flat_mesh(vb, tb)
        triangles = self.create_triangle_list(vb, tb)

        self.intersection_tests(10, triangles, mesh)

        mesh._isect_triangles_asm([runtime], "ray_triangles_idx", ren.assembler, ren.structures)
        mc = ren.assembler.assemble(self.asm_code1(ren))
        ds = runtime.load("test", mc)

        ray = self.random_ray()
        self.ray_ds(ds, ray, "ray1")
        self.flat_mesh_ds(ds, mesh, "mesh1")
        addr = mesh._grid._get_addr_in_array(0, 1, 2)
        print(addr)
        ds["ptr_triangles_arr"] = addr

        ntri = x86.GetUInt32(addr, 0, 0)
        triangles = x86.GetUInt32(addr+4, 0, ntri)
        hp = mesh.isect_triangles(ray, triangles)
        print(hp)
        if hp:
            print ("t=",hp.t)
            print ("hit=", hp.hit_point)
            print ("normala=", hp.normal)
        print(ntri)
        print(triangles)
        runtime.run("test")
        print("ret", ds["ret"])
        print("t= ", ds["t"])
        print("hit=", ds["hit"])
        print("normala", ds["normal"])

        start = time.clock()
        #self.speed_test(20, triangles, mesh)
        end = time.clock()
        #print(end-start)

       
if __name__ == "__main__":
    unittest.main()


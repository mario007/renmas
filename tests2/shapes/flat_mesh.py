import time
import unittest
from random import random
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

        start = time.clock()
        #self.speed_test(20, triangles, mesh)
        end = time.clock()
        print(end-start)

       
if __name__ == "__main__":
    unittest.main()


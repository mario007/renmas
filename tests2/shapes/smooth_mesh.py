
import time
import unittest
from random import random
import x86
from tdasm import Runtime
import renmas2

class SmoothMeshIsectTest(unittest.TestCase):
    def setUp(self):
        self.counter = 0

    def random_ray(self):
        factory = renmas2.Factory()
        #origin = (random(), random(), random())
        origin = (0.0, 0.0, 0.0)
        direction = (random(), random(), random())
        return factory.create_ray(origin, direction)

    def ray_ds(self, ds, ray, name):
        o = ray.origin
        d = ray.dir
        ds[name+ ".origin"] = (o.x, o.y, o.z, 0.0)
        ds[name+ ".dir"] = (d.x, d.y, d.z, 0.0)

    def smooth_mesh_ds(self, ds, mesh, name):
        ds[name + ".vertex_buffer_ptr"] = mesh._vb.addr()
        ds[name + ".vertex_size"] = mesh._vb.item_size()
        ds[name + ".triangle_buffer_ptr"] = mesh._tb.addr()
        ds[name + ".triangle_size"] = mesh._tb.item_size()
        bbox = mesh._grid.bbox
        ds[name + ".bbox_min"] = (bbox.x0, bbox.y0, bbox.z0, 0.0) 
        ds[name + ".bbox_max"] = (bbox.x1, bbox.y1, bbox.z1, 0.0)
        
        grid = mesh._grid
        nboxx = float(grid.nx / (bbox.x1 - bbox.x0))
        nboxy = float(grid.ny / (bbox.y1 - bbox.y0))
        nboxz = float(grid.nz / (bbox.z1 - bbox.z0))
        ds[name + ".nbox_width"] = (nboxx, nboxy, nboxz, 0.0)
        ds[name + ".n_1"] = (float(grid.nx-1), float(grid.ny-1), float(grid.nz-1), 0.0)
        ds[name + ".one_overn"] = (1.0 / grid.nx, 1.0 / grid.ny, 1.0 / grid.nz, 0.0)
        ds[name + ".grid_size"] = (grid.nx, grid.ny, grid.nz, 0)
        ds[name + ".grid_ptr"] = grid.asm_cells.ptr()
        ds[name + ".array_ptr"] = grid.lin_array.ptr()

    # eax = pointer to ray structure
    # ebx = pointer to flat mesh structure
    # ecx = pointer to minimum distance
    # edx = pointer to hitpoint 
    def asm_code1(self, ren):
        code = """
            #DATA
        """
        code += ren.structures.structs(('ray', 'smooth_mesh', 'hitpoint')) + """
            ray ray1
            smooth_mesh mesh1
            hitpoint hp1
            float min_dist = 99999.000
            uint32 ret

            #CODE
            mov eax, ray1
            mov ebx, mesh1
            mov ecx, min_dist
            mov edx, hp1
            call ray_smooth_mesh_intersection
            mov dword [ret], eax

            #END
        """
        return code

    def test_isect1(self):
        factory = renmas2.Factory()
        ren = renmas2.Renderer()
        runtime = Runtime()

        ply = renmas2.core.Ply()
        ply.load("I:/Ply_files/Horse97K.ply")
        vb = ply.vertex_buffer
        tb = ply.triangle_buffer
        mesh = factory.create_mesh(vb, tb)

        mesh.isect_asm([runtime], "ray_smooth_mesh_intersection", ren.assembler, ren.structures)
        mc = ren.assembler.assemble(self.asm_code1(ren))
        ds = runtime.load("test", mc)

        for i in range(1000):
            ray = self.random_ray()
            self.ray_ds(ds, ray, "ray1")
            self.smooth_mesh_ds(ds, mesh, "mesh1")
            runtime.run("test")
            hp = mesh.isect(ray)
            if hp:
                #print(hp.t, ds["hp1.t"])
                n1 = hp.normal
                n2 = ds["hp1.normal"]

                self.assertAlmostEqual(n1.x, n2[0], 3)
                self.assertAlmostEqual(n1.y, n2[1], 3)
                self.assertAlmostEqual(n1.z, n2[2], 3)


if __name__ == "__main__":
    unittest.main()



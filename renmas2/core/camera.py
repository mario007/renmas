
from .vector3 import Vector3
from .dynamic_array import DynamicArray
from .structures import Structures
import x86
from tdasm import Runtime
from ..macros import macro_call, assembler

class Camera:
    def __init__(self, eye, lookat, distance=100):
        self.eye = Vector3(float(eye[0]), float(eye[1]), float(eye[2]))
        self.lookat = Vector3(float(lookat[0]), float(lookat[1]), float(lookat[2]))
        self.up = Vector3(0.0, 1.0, 0.0)
        self.distance = float(distance) #distance of image plane form eye point
        self._compute_uvw()
        self.structures = Structures()
        self.ncore = 1
        self.python = True #Python or assembly version

        self._batch_rays = 100000
        self._allocate_array()
        self._runtime_arr = None

    def _compute_uvw(self):
        self.w = self.eye - self.lookat #w is in oposite direction of view
        self.w.normalize()
        self.u = self.up.cross(self.w)
        self.u.normalize()
        self.v = self.w.cross(self.u)
        #singularity
        if self.eye.x == self.lookat.x and self.eye.z == self.lookat.z and self.eye.y > self.lookat.y: #camera looking vertically down
            self.u = Vector3(0.0, 0.0, 1.0)
            self.v = Vector3(1.0, 0.0, 0.0)
            self.w = Vector3(0.0, 1.0, 0.0)

        if self.eye.x == self.lookat.x and self.eye.z == self.lookat.z and self.eye.y < self.lookat.y: #camera looking vertically up
            self.u = Vector3(1.0, 0.0, 0.0)
            self.v = Vector3(0.0, 0.0, 1.0)
            self.w = Vector3(0.0, -1.0, 0.0)

    def _allocate_array(self):
        self._ray_array = DynamicArray(self.structures.get_compiled_struct('ray'))
        self._ray_array.add_default_instances(self._batch_rays)

    def set_eye(self, x, y, z):
        self.eye = renmas.maths.Vector3(float(x), float(y), float(z))
        self._update_camera()

    def set_lookat(self, x, y, z):
        self.lookat = renmas.maths.Vector3(float(x), float(y), float(z))
        self._update_camera()

    def set_distance(self, distance):
        self.distance = float(distance)

    def _update_camera(self):
        self._compute_uvw()
        if self._runtime_arr is not None:
            for r in self._runtime_arr:
                ds = r.get_datasection('generate_rays')
                self._populate_data(ds)


    def set_ncore(self, n):
        nc = abs(int(n))
        if nc > 32: nc = 32 #max number of threads
        self.ncore = nc
        self._build_runtimes()
        self._update_camera()
    
    def show_ray(self, idx):
        sd = self._ray_array.get_instance(idx)
        eye = sd['origin']
        d = sd['dir']
        print('ex= %f ey= %f ez= %f' % (eye[0], eye[1], eye[2]))
        print('dx= %f dy= %f dz= %f' % (d[0], d[1], d[2]))

    def _build_runtimes(self):
        if self.python: return #python will generate samples
        self._runtime_arr = []
        adr = []
        for n in range(self.ncore):
            run = Runtime()
            macro_call.set_runtimes([run])
            mc = assembler.assemble(self._get_assembly_code())
            #mc.print_machine_code()
            run.load('generate_rays', mc)
            self._runtime_arr.append(run)
            adr.append(run.address_module('generate_rays'))
        self._exe_address = tuple(adr)

    def _get_assembly_code(self):
        raise NotImplementedError()

    def _populate_data(self, ds):
        raise NotImplementedError()

    def _generate_rays_python(self, nsamples, idx, sample_arr):
        raise NotImplementedError()

    def _onecore_asm(self, nsamples, idx, sample_arr):
        address = sample_arr.get_addr()
        sample_size = sample_arr.obj_size()
        address = address + sample_size * idx
        r = self._runtime_arr[0]
        ds = r.get_datasection('generate_rays')
        ds['nsamples'] = nsamples
        ds['adr_samples'] = address
        ds['adr_rays'] = self._ray_array.get_addr()
        r.run('generate_rays')

    
    def _twocore_asm(self, nsam1, nsam2, idx, sample_arr):
        address = sample_arr.get_addr()
        sample_size = sample_arr.obj_size()

        adr1 = address + sample_size * idx
        adr2 = address + sample_size * (idx + nsam1)

        r1 = self._runtime_arr[0]
        r2 = self._runtime_arr[1]
        ds = r1.get_datasection('generate_rays')
        ds['nsamples'] = nsam1  
        ds['adr_samples'] = adr1 
        ds['adr_rays'] = self._ray_array.get_addr()
        ds = r2.get_datasection('generate_rays')
        ds['nsamples'] = nsam2 
        ds['adr_samples'] = adr2
        ray_size = self._ray_array.obj_size()
        ds['adr_rays'] = self._ray_array.get_addr() + nsam1 * ray_size 
        x86.ExecuteModules(self._exe_address[0:2])
        #print(nsam1, nsam2)

    def generate_rays(self, nsamples, idx, sample_arr):

        if self.python:
            self._generate_rays_python(nsamples, idx, sample_arr)
        else: #first just 1 core 
            if self.ncore == 1:
                self._onecore_asm(nsamples, idx, sample_arr)
            elif self.ncore == 2:
                m1 = nsamples // 2
                p = nsamples % 2
                m2 = m1 + p 
                if m1 == 0:
                    self._onecore_asm(nsamples, idx, sample_arr)
                else:
                    self._twocore_asm(m1, m2, idx, sample_arr)


    def python_version(self, version=True):
        self.python = version 
        if not version:
            self._build_runtimes()
            self._update_camera()


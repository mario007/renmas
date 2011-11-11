
import x86
from ..core import Camera 
from ..macros import macro_call, assembler

class Pinhole(Camera):
    def __init__(self, eye, lookat, distance=100):
        super(Pinhole, self).__init__(eye, lookat, distance)

    def generate_ray(self, sample, origin, direction):
        x, y = x86.GetFloat(sample, 0, 2)
        d = self.u * x + self.v * y - self.w * self.distance
        d.normalize()

        x86.SetFloat(origin, (self.eye.x, self.eye.y, self.eye.z, 0.0), 0)
        x86.SetFloat(direction, (d.x, d.y, d.z, 0.0), 0)

    #in eax is pointer to sample structure
    def generate_ray_asm(self, runtimes, label):
        asm_structs = self.structures.get_struct('ray')
        asm_structs += self.structures.get_struct('sample')

        code = """
            #DATA
        """
        code += asm_structs + """
            float u[4] 
            float v[4]
            float wdistance[4]
            float eye[4]


            #CODE
        """
        code += "global " + label + ":\n" + """
            
            macro eq128 xmm0 = eax.sample.xyxy 
            macro broadcast xmm1 = xmm0[0]
            macro eq128 xmm3 = u * xmm1
            macro broadcast xmm2 = xmm0[1]
            macro eq128 xmm4 = v * xmm2
            macro eq128 xmm5 = xmm3 + xmm4 - wdistance
            macro normalization xmm5 {xmm6, xmm7}
            
            macro eq128 eax.sample.cam_ray.origin = eye {xmm0}
            macro eq128 eax.sample.cam_ray.dir = xmm5 {xmm0}
            ret

        """
        macro_call.set_runtimes(runtimes)
        mc = assembler.assemble(code, True)
        self._ds = []
        for r in runtimes:
            ds = r.load("generate_ray", mc) 
            self._ds.append(ds)

        self._update_data()

    def _update_data(self):
        if self._ds is None: return
        for ds in self._ds:
            u = self.u
            v = self.v
            wd = self.w * self.distance
            eye = self.eye
            ds["u"] = (u.x, u.y, u.z, 0.0) 
            ds["v"] = (v.x, v.y, v.z, 0.0)
            ds["wdistance"] = (wd.x, wd.y, wd.z, 0.0)
            ds["eye"] = (eye.x, eye.y, eye.z, 0.0)


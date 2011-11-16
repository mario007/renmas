
from ..core import get_structs, Ray 
from ..macros import macro_call, assembler
from .camera import Camera

class Pinhole(Camera):
    def __init__(self, eye, lookat, distance=100):
        super(Pinhole, self).__init__(eye, lookat, distance)

    def ray(self, sample):
        direction = self.u * sample.x + self.v * sample.y - self.w * self.distance
        direction.normalize()
        return Ray(self.eye, direction)

    #eax - pointer to sample structure
    #ebx - pointer to ray structure
    def ray_asm(self, runtimes, label):
        asm_structs = get_structs(('ray', 'sample'))
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
            
            macro eq128 ebx.ray.origin = eye {xmm7}
            macro eq128 ebx.ray.dir = xmm5 {xmm7}
            ret

        """
        macro_call.set_runtimes(runtimes)
        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        self._ds = []
        name = "ray" + str(hash(self))
        for r in runtimes:
            ds = r.load(name, mc) 
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


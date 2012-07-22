
from ..core import Ray 
from .camera import Camera
from ..core.structures import RAY, SAMPLE

class Pinhole(Camera):
    def __init__(self, eye, lookat, distance=100):
        super(Pinhole, self).__init__(eye, lookat, distance)
        self._ds = None

    def ray(self, sample):
        direction = self.u * sample.x + self.v * sample.y - self.w * self.distance
        direction.normalize()
        return Ray(self.eye, direction)

    #eax - pointer to sample structure
    #ebx - pointer to ray structure
    def ray_asm(self, runtimes, label, assembler):
        asm_structs = RAY + SAMPLE
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
        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        self._ds = []
        name = "get_ray" + str(id(self))
        #TODO check if global label allready exitsts!!!
        for r in runtimes:
            ds = r.load(name, mc) 
            self._ds.append(ds)

        self._update_data()

    def _update_data(self):
        if self._ds is None: 
            return
        for ds in self._ds:
            wd = self.w * self.distance
            ds['u'] = self.u.to_ds()
            ds['v'] = self.v.to_ds()
            ds["wdistance"] = wd.to_ds()
            ds['eye'] = self.eye.to_ds()


import renmas.core
import renmas.maths
import renmas.utils as util

class PinholeCamera:
    def __init__(self, eye, lookat, distance=100):
        self.eye = eye
        self.lookat = lookat
        self.up = renmas.maths.Vector3(0.0, 1.0, 0.0)
        self.distance = distance #distance of image plane form eye point
        self.ds = None
        self.compute_uvw()

    def compute_uvw(self):
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

    def ray(self, sample):
        direction = self.u * sample.x + self.v * sample.y - self.w * self.distance
        direction.normalize()
        return renmas.core.Ray(self.eye, direction)

    def ray_asm(self, runtime, label):

        asm_structs = util.structs("ray", "sample")
        ASM = """
        #DATA
        """
        
        if util.AVX:
            code = """
                vdpps xmm5, xmm4, xmm4, 0x7F
                vsqrtps xmm5, xmm5
            """
        elif util.SSE41:
            code = """
                movaps xmm5, xmm4
                dpps xmm5, xmm5, 0x7F 
                sqrtps xmm5, xmm5
            """
        else:
            code = """
                macro dot xmm5 = xmm4 * xmm4
                macro broadcast xmm5 = xmm5[0]
                sqrtps xmm5, xmm5
            """

        # eax pointer to ray structure
        # ebx pointer to sample structure
        ASM += asm_structs + """
            float u[4] 
            float v[4]
            float wdistance[4]
            float eye[4]

        #CODE
        """
        ASM += " global " + label + ":\n" + """
        macro eq128 xmm0 = ebx.sample.xyxy
        macro broadcast xmm1 = xmm0[0]
        macro eq128 xmm2 = xmm1 * u {xmm0}
        macro broadcast xmm0 = xmm0[1]
        macro eq128 xmm3 = xmm0 * v {xmm2} 
        macro eq128 xmm4 = xmm2 + xmm3
        macro eq128 xmm4 = xmm4 - wdistance
        """
        ASM += code + """
            macro eq128 xmm4 = xmm4 / xmm5
            macro eq128_128 eax.ray.dir = xmm4, eax.ray.origin = eye
        ret

        """

        assembler = util.get_asm()
        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "generate_ray" + str(util.unique())
        self.ds = runtime.load(name, mc)
        self._populate_ds()

    def _populate_ds(self):
        if self.ds is None: return
        u = self.u
        v = self.v
        wd = self.w * self.distance
        eye = self.eye
        self.ds["u"] = (u.x, u.y, u.z, 0.0) 
        self.ds["v"] = (v.x, v.y, v.z, 0.0)
        self.ds["wdistance"] = (wd.x, wd.y, wd.z, 0.0)
        self.ds["eye"] = (eye.x, eye.y, eye.z, 0.0)



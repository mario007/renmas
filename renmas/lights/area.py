
import renmas.core
import renmas.shapes
import renmas.utils as util

class AreaLight:
    def __init__(self, spectrum, shape):
        self.shape = shape 
        self.spectrum = spectrum

    def set_shape(self, shape):
        self.shape = shape

    def L(self, hitpoint):
        # 1. check visibility
        # 2. populate light vector in hitpoint and spectrum of light
        
        self.shape.light_sample(hitpoint)
        position = hitpoint.light_sample
        
        wi = position - hitpoint.hit_point
        len2 = wi.length_squared()
        wi.normalize()
        
        wout = wi * -1.0
        cos_light = wout.dot(hitpoint.light_normal)
        spectrum = self.spectrum * cos_light * (1.0 / (hitpoint.light_pdf * len2))

        ndotwi = hitpoint.normal.dot(wi)
        hitpoint.wi = wi 
        hitpoint.ndotwi = ndotwi
        if ndotwi < 0.0: # ray strike back of object so that mean point is not visible to light. dielectric?? FIXME
            hitpoint.visible = False
            return False

        ret = renmas.shapes.visible(position, hitpoint.hit_point)
        if ret is False:
            hitpoint.visible = False
            return False
        else: #think copy of spectrum ?? FIXME
            hitpoint.spectrum = spectrum #TODO reduce intesity, attenuation options  1/r^2
            hitpoint.visible = True
            return True

    def L_asm(self, runtime, visible_label):
        
        self.shape.light_sample_asm(runtime)

        #eax - pointer to hitpoint structure
        asm_structs = renmas.utils.structs("hitpoint")
        ASM = """
        #DATA
        """
        ASM += asm_structs + """
        float spectrum[4]
        float minus_one[4] = -1.0, -1.0, -1.0, 0.0
        float tmp_spectrum[4] = 0.0, 0.0, 0.0, 0.0
        float zero = 0.0
        uint32 ptr_sample

        ; temp variables need for shading of light
        ; later you can try using stack for this, dynamic aligment is required!
        uint32 ptr_hp

        #CODE
        mov dword [ptr_hp], eax ; save pointer to hitpoint
        call dword [ptr_sample]
        mov eax, dword [ptr_hp]

        macro eq128 xmm0 = eax.hitpoint.light_sample - eax.hitpoint.hit 
        macro dot xmm4 = xmm0 * xmm0
        """
        ASM += util.normalization("xmm0", "xmm1", "xmm2") + """
        macro eq128 xmm5 = xmm0 * minus_one {xmm4}
        macro dot xmm6 = xmm5 * eax.hitpoint.light_normal {xmm0, xmm4} 

        macro eq128 xmm7 = spectrum {xmm0}
        macro eq32 xmm4 = xmm4 * eax.hitpoint.light_pdf {xmm0}
        macro eq32 xmm6 = xmm6 / xmm4 {xmm0}
        macro broadcast xmm6 = xmm6[0]
        macro eq128 xmm7 = xmm7 * xmm6
        macro eq128 tmp_spectrum = xmm7

        macro dot xmm1 = xmm0 * eax.hitpoint.normal
        macro if xmm1 < zero goto reject  

        macro eq128 eax.hitpoint.wi = xmm0
        macro eq32 eax.hitpoint.ndotwi = xmm1
        ; test visibility of two points
        macro eq128 xmm0 = eax.hitpoint.light_sample 
        macro eq128 xmm1 = eax.hitpoint.hit
        """
        ASM += "call " + visible_label + "\n" + """
        cmp eax, 1
        jne reject
        mov eax, dword [ptr_hp]

        macro eq128 eax.hitpoint.spectrum = tmp_spectrum
        mov dword [eax + hitpoint.visible], 1
        ret

        reject:
        mov eax, dword [ptr_hp]
        mov dword [eax + hitpoint.visible], 0
        ret
        """

        assembler = util.get_asm()
        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "arealight_L" + str(util.unique())

        self.ds = runtime.load(name, mc)
        self._populate_ds()

        #FIXME - add method to runtime class so we can ask runtime for address of module
        self.func_ptr = runtime.modules[name][0]

    def _populate_ds(self):
        if self.ds is None: return
        self.ds["ptr_sample"] = self.shape.sample_ptr
        s = self.spectrum
        self.ds["spectrum"] = (s.r, s.g, s.b, 0.0)



import renmas.core
import renmas.shapes
import renmas.utils as util


class PointLight:
    def __init__(self, position, spectrum):
        self.position = position
        self.spectrum = spectrum

        #asm stuff
        self.ds = None
        self.func_ptr = None # function pointer

    def L(self, hitpoint):
        # 1. check visibility
        # 2. populate light vector in hitpoint and spectrum of light
        
        wi = self.position - hitpoint.hit_point
        wi.normalize()
        ndotwi = hitpoint.normal.dot(wi)
        if ndotwi < 0.0: # ray strike back of object so that mean point is not visible to light. dielectric?? FIXME
            hitpoint.visible = False
            return False

        ret = renmas.shapes.visible(self.position, hitpoint.hit_point)
        if ret is False:
            hitpoint.visible = False
            return False
        else: #think copy of spectrum ?? FIXME
            hitpoint.spectrum = self.spectrum #TODO reduce intesity, attenuation options  1/r^2
            hitpoint.visible = True
            hitpoint.wi = wi 
            hitpoint.ndotwi = ndotwi
            return True

    def L_asm(self, runtime, visible_label):
        
        #eax - pointer to hitpoint structure
        asm_structs = renmas.utils.structs("hitpoint")
        ASM = """
        #DATA
        """
        ASM += asm_structs + """
        float position[4]
        float spectrum[4]
        float zero = 0.0

        ; temp variables need for shading of light
        ; later you can try using stack for this, dynamic aligment is required!
        uint32 ptr_hp

        #CODE
        mov dword [ptr_hp], eax ; save pointer to hitpoint
        macro eq128 xmm0 = position - eax.hitpoint.hit 
        """
        ASM += util.normalization("xmm0", "xmm1", "xmm2") + """
        macro dot xmm1 = xmm0 * eax.hitpoint.normal
        macro if xmm1 < zero goto reject  

        macro eq128 eax.hitpoint.wi = xmm0
        macro eq32 eax.hitpoint.ndotwi = xmm1
        ; test visibility of two points
        macro eq128 xmm0 = position
        macro eq128 xmm1 = eax.hitpoint.hit
        """
        ASM += "call " + visible_label + "\n" + """
        cmp eax, 1
        jne reject
        mov eax, dword [ptr_hp]
        macro eq128 eax.hitpoint.spectrum = spectrum
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
        name = "pointlight_L" + str(util.unique())

        self.ds = runtime.load(name, mc)
        self._populate_ds()

        #FIXME - add method to runtime class so we can ask runtime for address of module
        self.func_ptr = runtime.modules[name][0]

    def _populate_ds(self):
        if self.ds is None: return
        p = self.position
        self.ds["position"] = (p.x, p.y, p.z, 0.0)
        s = self.spectrum
        self.ds["spectrum"] = (s.r, s.g, s.b, 0.0)


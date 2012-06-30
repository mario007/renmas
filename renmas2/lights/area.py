
from .light import Light

class AreaLight(Light):
    def __init__(self, shape, material):
        self.shape = shape
        self.material = material

    def L(self, hitpoint, renderer):

        if not self.shape.light_sample(hitpoint): #shape doesn't support area light
            hitpoint.visible = False
            return False

        wi = hitpoint.light_sample - hitpoint.hit_point
        len2 = wi.length_squared()
        wi.normalize()

        cos_light = wi.dot(hitpoint.light_normal * -1.0)
        
        if self.material.emission is None:
            hitpoint.visible = False
            return False

        spectrum = self.material.emission * (cos_light / (hitpoint.light_pdf * len2))

        ndotwi = hitpoint.normal.dot(wi)
        hitpoint.wi = wi 
        hitpoint.ndotwi = ndotwi
        if ndotwi < 0.0: # ray strike back of object so that mean point is not visible to light. dielectric?? FIXME
            hitpoint.visible = False
            return False

        ret = renderer._intersector.visibility(hitpoint.light_sample, hitpoint.hit_point)
        if ret:
            hitpoint.l_spectrum = spectrum
            hitpoint.visible = True
            return True
        else:
            hitpoint.visible = False
            return False

    #eax - pointer to hitpoint structure
    #TODO - this is not implement 
    def L_asm(self, runtimes, visible_label, assembler, structures):

        code = "\n #DATA \n" + structures.structs(('hitpoint',)) + """
        float position[4]
        spectrum l_spectrum
        float zero = 0.0
        uint32 ptr_hp
        #CODE
        mov dword [ptr_hp], eax ; save pointer to hitpoint
        macro eq128 xmm0 = position - eax.hitpoint.hit 
        macro normalization xmm0 {xmm6, xmm7}
        macro dot xmm1 = xmm0 * eax.hitpoint.normal {xmm6, xmm7}
        macro if xmm1 < zero goto reject  

        macro eq128 eax.hitpoint.wi = xmm0 {xmm0}
        macro eq32 eax.hitpoint.ndotwi = xmm1 {xmm1}
        ; test visibility of two points
        macro eq128 xmm0 = position
        macro eq128 xmm1 = eax.hitpoint.hit
        """
        code += "call " + visible_label + "\n" + """
        cmp eax, 1
        jne reject
        mov eax, dword [ptr_hp]
        mov dword [eax + hitpoint.visible], 0
        lea ecx, dword [eax + hitpoint.l_spectrum]
        mov ebx, l_spectrum
        macro spectrum ecx = ebx
        ret

        reject:
        mov eax, dword [ptr_hp]
        mov dword [eax + hitpoint.visible], 0
        ret
        """

        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        self.l_asm_name = name = "pointlight_L" + str(hash(self))
        self._ds = []
        for r in runtimes:
            self._ds.append(r.load(name, mc)) 
        self._populate_ds()

    def _populate_ds(self):
        return
        for ds in self._ds:
            p = self._position
            ds["position"] = (p.x, p.y, p.z, 0.0)
            s = self._spectrum * self._intesity_scale
            ds["l_spectrum.values"] = s.to_ds()


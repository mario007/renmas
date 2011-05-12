import random
from .hitpoint import HitPoint
import renmas.utils as util
from renmas.maths import Vector3

class Plane:
    def __init__(self, point, normal, material):
        self.point = point
        self.normal = normal.normalize()
        self.material = material

    def intersect(self, ray, min_dist = 999999.0):
        temp = (self.point - ray.origin).dot(self.normal)
        temp2 = ray.dir.dot(self.normal)
        if temp2 == 0.0: return False
        temp3 = temp / temp2
        if temp3 > 0.00001 and temp3 < min_dist:
            hit_point = ray.origin + ray.dir * temp3
            return HitPoint(temp3, hit_point, self.normal, self.material, ray)
        else:
            return False

    @classmethod
    def intersect_asm(cls, runtime, label_name):

        asm_structs = util.structs("ray", "plane", "hitpoint")

        ASM = """
        #DATA
        float epsilon = 0.0001
        """
        ASM += asm_structs + """
            ;eax = pointer to ray structure
            ;ebx = pointer to plane structure
            ;ecx = pointer to minimum distance
            ;edx = pointer to hitpoint
        #CODE
        """
        ASM += " global " + label_name + ":\n" + """
            macro eq128 xmm0 = ebx.plane.normal
            macro dot xmm1 = eax.ray.dir * xmm0 
            macro eq128 xmm2 = ebx.plane.point - eax.ray.origin {xmm0, xmm1}
            macro dot xmm3 = xmm2 * xmm0 {xmm1}
            macro eq32 xmm4 = xmm3 / xmm1

            macro if xmm4 > epsilon goto populate_hitpoint
            mov eax, 0 
            ret
            
            populate_hitpoint:
            ; in ecx is minimum distance
            macro if xmm4 > ecx goto _reject 
            macro broadcast xmm5 = xmm4[0]
            macro eq128_128 edx.hitpoint.normal = ebx.plane.normal, xmm6 = xmm5 * eax.ray.dir 
            macro eq32 edx.hitpoint.t = xmm4 {xmm6}
            macro eq32_128 edx.hitpoint.mat_index = ebx.plane.mat_index, edx.hitpoint.hit = xmm6 + eax.ray.origin
            mov eax, 1
            ret

            _reject:
            mov eax, 0
            ret
        """

        assembler = util.get_asm()
        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        runtime.load("ray_plane_intersection", mc)

    @classmethod
    def intersectbool_asm(cls, runtime, label_name):

        asm_structs = util.structs("ray", "plane", "hitpoint")

        ASM = """
        #DATA
        float epsilon = 0.0001
        """
        ASM += asm_structs + """
            ;eax = pointer to ray structure
            ;ebx = pointer to plane structure
            ;ecx = pointer to minimum distance
        #CODE
        """
        ASM += " global " + label_name + ":\n" + """
            macro eq128 xmm0 = ebx.plane.normal
            macro dot xmm1 = eax.ray.dir * xmm0 
            macro eq128 xmm2 = ebx.plane.point - eax.ray.origin {xmm0, xmm1}
            macro dot xmm3 = xmm2 * xmm0 {xmm1}
            macro eq32 xmm4 = xmm3 / xmm1

            macro if xmm4 > epsilon goto populate_hitpoint
            mov eax, 0 
            ret
            
            populate_hitpoint:
            ; in ecx is minimum distance
            macro if xmm4 > ecx goto _reject 
            mov eax, 1
            ret

            _reject:
            mov eax, 0
            ret
        """

        assembler = util.get_asm()
        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        runtime.load("ray_plane_intersection_bool", mc)

    @classmethod
    def intersect_array_asm(cls, runtime, lbl_arr_intersect, lbl_ray_intersect):
        asm_structs = util.structs("ray", "plane", "hitpoint")

        ASM = """
        #DATA
        """
        ASM += asm_structs + """
        #CODE
        """
        ASM += " global " + lbl_arr_intersect + ":\n" + """
          ; eax - ray, ebx - hp , ecx - min_dist, esi - ptr_planes, edi - nplanes
        ;plane_array:
        push ecx
        push eax
        push ebx
        push esi
        push edi

        _plane_loop:
        mov eax, dword [esp + 12] ; mov eax, ray
        mov ebx, dword [esp + 4] ; mov ebx, plane 
        mov ecx, dword [esp + 16]; address of minimum distance
        mov edx, dword [esp + 8] ; mov edx, hp
        """
        ASM += " call " + lbl_ray_intersect + "\n" + """
        ;call _plane_intersect 
        cmp eax, 0  ; 0 - no intersection ocur
        je _next_plane
        mov eax, dword [esp + 8]
        mov ebx, dword [eax + hitpoint.t]

        mov edx, dword [esp + 16] ;populate new minimum distance
        mov dword [edx], ebx

        _next_plane:
        sub dword [esp], 1  
        jz _end_plane
        add dword [esp + 4], sizeof plane 
        jmp _plane_loop
        
        _end_plane:
        add esp, 20 
        ret
        """

        assembler = util.get_asm()
        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        runtime.load("ray_plane_array_intersection", mc)


    @classmethod
    def generate_plane(cls):
        x = random.random() * 10.0
        y = random.random() * 10.0
        z = random.random() * 10.0
        dir_x = random.random() * 10.0 - 5.0
        dir_y = random.random() * 10.0 - 5.0
        dir_z = random.random() * 10.0 - 5.0

        point = Vector3(x, y, z)
        normal = Vector3(dir_x, dir_y, dir_z)
        normal.normalize()

        plane = Plane(point, normal, None)
        return plane

    @classmethod
    def struct(cls):
        asm_code = """ #DATA
        """
        asm_code += util.structs("plane") 
        asm_code += """
        #CODE
        #END
        """
        mc = util.get_asm().assemble(asm_code)
        return mc.get_struct("plane")

    def struct_params(self):
        d = {}
        d["point"] = (self.point.x, self.point.y, self.point.z, 0.0)
        d["normal"] = (self.normal.x, self.normal.y, self.normal.z, 0.0)
        if self.material is None:
            d["mat_index"] = 999999 #FIXME - think to solve this in better way
        return d


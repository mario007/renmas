
import x86
from tdasm import Tdasm, Runtime
import renmas
import renmas.utils as util
from renmas.maths import Vector3
from .grid_mesh import GridMesh
import time
import math

class VertexType:
    def __init__(self, normal=None, uv=None):
        self.normal = bool(normal)
        self.uv = bool(uv)

    def has_normal(self, yes):
        return self.normal

    def has_uv(self, yes):
        return self.uv

class VertexBuffer:
    def __init__(self, vertex_type=None, reserve=0):
        #size of vertex dependes on type
        self.size = 0
        self.vertex_type = vertex_type 
        self.reserve = reserve
        if vertex_type is None:
            self.vertex_size = 16 #store x, y, z, xx(aligment)
        else:
            if vertex_type.has_normal():
                self.normal_offset = 16
                self.vertex_size = 32 # store x,y,z,xx for vertex and than x,y,z,xx for normal 

        if self.reserve > 0:
            self.address = x86.MemData(self.reserve*self.vertex_size)
        else:
            self.address = None

    def vsize(self):
        return self.vertex_size

    def addr(self):
        return self.address.ptr()  

    def nvertices(self):
        return self.size

    def clear_buffer(self):
        self.address = None
        self.size = 0
        self.reserve = 0

    def add_vertex(self, x, y, z, normal=None, uv=None): #TODO normal - nx, ny, nz dont't use Vector3
        if self.address is None:
            self.address = x86.MemData(self.vertex_size)
            self.reserve += 1
        elif self.reserve == self.size:
            if self.size > 0 and self.size <= 100:
                self.reserve += 1
            elif self.size > 100 and self.size <= 10000:
                self.reserve += 100
            elif self.size > 10000 and self.size <= 1000000:
                self.reserve += 10000
            else:
                self.reserve += 100000

            temp = x86.MemData(self.vertex_size*self.reserve)
            util.memcpy(temp.ptr(), self.address.ptr(), self.size*self.vertex_size) 
            self.address = temp

        #x = x * 3.0
        #y = y * 3.0
        #z = z * 3.0
        offset = self.vertex_size * self.size
        x86.SetFloat(self.address.ptr()+offset, (x, y, z, 0.0), 0)
        if normal is not None:
            #print("Not tested") TODO
            offset = offset + self.normal_offset
            x86.SetFloat(self.address.ptr()+offset, (normal.x, normal.y, normal.z, 0.0), 0)
        self.size += 1

    def edit_position(self, index, x, y, z):
        addr = self.address.ptr() + index * self.vertex_size 
        x86.SetFloat(addr, (x, y, z, 0.0), 0)

    def get_position(self, index):
        addr = self.address.ptr() + index * self.vertex_size 
        position = x86.GetFloat(addr, 0, 3)
        return position

    def get_normal(self, index):
        addr = self.address.ptr() + index * self.vertex_size + self.normal_offset 
        normal = x86.GetFloat(addr, 0, 3)
        return normal 

    def get_uv(self, index):
        pass

class Triangles:
    def __init__(self, reserve=0):
        # v0, v1, v2, material, normal
        self.size = 0
        self.reserve = reserve
        self.tri_size = 32 

        if self.reserve > 0:
            self.address = x86.MemData(self.reserve*self.tri_size)
        else:
            self.address = None

    def add_triangle(self, v0, v1, v2, material, nx, ny, nz):
        if self.address is None:
            self.address = x86.MemData(self.tri_size)
            self.reserve += 1
        elif self.reserve == self.size:
            if self.size > 0 and self.size <= 100:
                self.reserve += 1
            elif self.size > 100 and self.size <= 10000:
                self.reserve += 100
            elif self.size > 10000 and self.size <= 1000000:
                self.reserve += 10000
            else:
                self.reserve += 100000

            temp = x86.MemData(self.tri_size*self.reserve)
            util.memcpy(temp.ptr(), self.address.ptr(), self.size*self.tri_size) 
            self.address = temp

        offset = self.tri_size * self.size
        x86.SetInt32(self.address.ptr()+offset, (v0, v1, v2, material), 0)
        offset = offset + 16 # offset to normal
        x86.SetFloat(self.address.ptr()+offset, (nx, ny, nz, 0.0), 0)
        self.size += 1

    def tsize(self):
        return self.tri_size

    def addr(self):
        return self.address.ptr()  

    def get_vertices(self, index):
        addr = self.address.ptr() + index * self.tri_size 
        return x86.GetInt32(addr, 0, 3)

    def get_normal(self, index):
        addr = self.address.ptr() + index * self.tri_size 
        addr = addr + 16
        return x86.GetFloat(addr, 0, 3)

    def get_material(self, index):
        addr = self.address.ptr() + index * self.tri_size 
        addr = addr + 12 # offset to materail index
        return x86.GetInt32(addr, 0, 0)

def calc_normal(vb, v0, v1, v2, bbox):
    #p0 = vb.get_position(v0)
    #p1 = vb.get_position(v1)
    #p2 = vb.get_position(v2)
    #ver0 = Vector3(p0[0], p0[1], p0[2])
    #ver1 = Vector3(p1[0], p1[1], p1[2])
    #ver2 = Vector3(p2[0], p2[1], p2[2])

   
    x1, y1, z1 = vb.get_position(v0)
    x2, y2, z2 = vb.get_position(v1)
    x3, y3, z3 = vb.get_position(v2)

    epsilon = 0.0001
    minx = min(min(x1, y1), z1) - epsilon
    maxx = max(max(x1, y1), z1) + epsilon
    miny = min(min(x2, y2), z2) - epsilon
    maxy = max(max(x2, y2), z2) + epsilon
    minz = min(min(x3, y3), z3) - epsilon
    maxz = max(max(x3, y3), z3) + epsilon

    if minx < bbox.x0: bbox.x0 = minx 
    if miny < bbox.y0: bbox.y0 = miny
    if minz < bbox.z0: bbox.z0 = minz

    if maxx > bbox.x1: bbox.x1 = maxx
    if maxy > bbox.y1: bbox.y1 = maxy
    if maxz > bbox.z1: bbox.z1 = maxz

    u1, u2, u3 = x2 - x1, y2 - y1, z2 - z1
    v1, v2, v3 = x3 - x1, y3 - y1, z3 - z1
    #cross product
    n1 = u2 * v3 - u3 * v2
    n2 = u3 * v1 - u1 * v3
    n3 = u1 * v2 - u2 * v1
    
    #normalize n
    dotn = n1 * n1 + n2 * n2 + n3 * n3
    length = math.sqrt(dotn)
    if length:
        n1 = n1 / length
        n2 = n2 / length
        n3 = n3 / length
    return (n1, n2, n3)
    
    #normal = (ver1 - ver0).cross(ver2 - ver0)
    #return normal.normalize()

def extend_bbox(vb, v0, v1, v2, bbox):
    p0 = vb.get_position(v0)
    p1 = vb.get_position(v1)
    p2 = vb.get_position(v2)

    epsilon = 0.0001
    minx = min(min(p0[0], p1[0]), p2[0]) - epsilon
    maxx = max(max(p0[0], p1[0]), p2[0]) + epsilon
    miny = min(min(p0[1], p1[1]), p2[1]) - epsilon
    maxy = max(max(p0[1], p1[1]), p2[1]) + epsilon
    minz = min(min(p0[2], p1[2]), p2[2]) - epsilon
    maxz = max(max(p0[2], p1[2]), p2[2]) + epsilon

    if minx < bbox.x0: bbox.x0 = minx 
    if miny < bbox.y0: bbox.y0 = miny
    if minz < bbox.z0: bbox.z0 = minz

    if maxx > bbox.x1: bbox.x1 = maxx
    if maxy > bbox.y1: bbox.y1 = maxy
    if maxz > bbox.z1: bbox.z1 = maxz


class Mesh3D:
    def __init__(self, material):
        self.triangles = None
        self.vertex_buffer = None
        self.material = material #default material 
        p0 = Vector3(9999999.0, 9999999.0, 9999999.0)
        p1 = Vector3(-9999999.0, -9999999.0, -9999999.0)
        import renmas.shapes
        self.bounding_box = renmas.shapes.BBox(p0, p1, None) 
        self.grid = None
        self.ptr_isect = None

    def load_ply(self, fname, material=None):
        if material is None:
            material = self.material

        start = time.clock()
        lst_elements = [] # list of elements in file
        dict_property = {} 
        f = open(fname, 'r')
        #first line must be 'ply' magic number
        ply = f.readline().strip()
        if ply != "ply":
            raise ValueError("This is not valid ply file format!")
        print("Processing header")
        for line in f:
            words = line.split()
            #ignore empty lines and comments and finish header on end_header keyword
            if len(words) == 0: continue
            if words[0] == "comment": continue
            if words[0] == "end_header": break

            if words[0] == "format":
                if words[1] == "ascii": 
                    typ_file = "ASCII"
                elif words[1] == "binary_big_endian":
                    typ_file = "BE"
                elif words[1] == "binary_little_endian":
                    typ_file = "LE"
                version = words[2]
            elif words[0] == "element":
                element = (words[1], int(words[2]))
                lst_elements.append(element)
                dict_property[element] = []

            elif words[0] == "property":
                if words[1] == "list":
                    prop = (words[2], words[3], "list")
                    dict_property[lst_elements[-1]].append(prop)
                else:
                    prop = (words[1], words[2])
                    dict_property[lst_elements[-1]].append(prop)

        #create vertex buffer of specifed type TODO
        if self.vertex_buffer is None:
            self.vertex_buffer = VertexBuffer()
        if self.triangles is None:
            self.triangles = Triangles()

        print("Processing reast of file")
        for elem in lst_elements:
            if elem[0] == "vertex":
                nvertex = elem[1]
                num = 0
                start1 = time.clock()
                for line in f:
                    words = line.split()
                    if len(words) == 0: continue
                    #read veretex TODO -- vertex normal and uv kordinates
                    x = float(words[0])
                    y = float(words[1])
                    z = float(words[2])
                    self.vertex_buffer.add_vertex(x, y, z)

                    num += 1
                    if num == nvertex: break # we finish read all vertices
                end1 = time.clock()
                print("Ucitavanje vertexa je trajalo ", end1-start1)

            if elem[0] == "face":
                nfaces = elem[1]
                num = 0
                for line in f:
                    words = line.split()
                    if len(words) == 0: continue
                    nindices = int(words[0])
                    if nindices == 3:
                        v0 = int(words[1])
                        v1 = int(words[2])
                        v2 = int(words[3])
                        #calculate normal fot triangle if not specified in file TODO
                        normal = calc_normal(self.vertex_buffer, v0, v1, v2, self.bounding_box)
                        self.triangles.add_triangle(v0, v1, v2, material, normal[0], normal[1], normal[2])
                        # if normal for vertices exists use that use that to calculate normal of triangle TODO
                        
                        #print(v0, v1, v2)
                    elif nindices == 4:
                        v0 = int(words[1])
                        v1 = int(words[2])
                        v2 = int(words[3])
                        normal = calc_normal(self.vertex_buffer, v0, v1, v2, self.bounding_box)
                        self.triangles.add_triangle(v0, v1, v2, material, normal[0], normal[0], normal[0])


                        v3 = int(words[3]) #not confirmed that this is good!!!
                        v4 = int(words[4])
                        v5 = int(words[0])
                        normal = calc_normal(self.vertex_buffer, v3, v4, v0, self.bounding_box)
                        self.triangles.add_triangle(v3, v4, v0, material, normal[0], normal[0], normal[0])
                    else:
                        raise ValueError("Its two many numbers for faces. Only 3 and 4 is accepted! :-)")

                    num += 1
                    if num == nfaces: break # we finish read all vertices

            #ignore othere elements for now

        print ("Tip fajla = ", typ_file, " Version = ", version)
        print (lst_elements)
        print (dict_property)
        print (nvertex, nfaces)
        print (self.triangles.size)
        bb = self.bounding_box
        end = time.clock()
        print("Ucitavanje ", fname, " je trajalo ", end-start)

        #for x in range(nfaces):
        #    print (self.triangles.get_vertices(x))
        #    print (self.triangles.get_normal(x))
        #    print (self.triangles.get_material(x))

    def prepare_isect(self): #construct GridMesh
        self.grid = GridMesh()
        start = time.clock()
        self.grid.setup(self) #construction of meshgird happens here
        end = time.clock()
        print("Generiranje grida je trajalo ", end-start)

        self.runtime = Runtime()
        self.prepare_isect_asm(self.runtime)

    def load_obj(self, fname, material=None):
        pass

    def bbox(self):
        return self.bounding_box

    def isect_triangles(self, ray, lst_triangles, min_dist = 999999.0):
        hit_point = None
        for idx in lst_triangles:
            hit = self.ray_tri(ray, idx, min_dist) 
            if hit is False: continue
            if hit.t < min_dist:
                min_dist = hit.t
                hit_point = hit
        return hit_point

    def ntriangles(self):
        return self.triangles.size

    def bbox_tri(self, idx):
        v0, v1, v2 = self.triangles.get_vertices(idx)

        vb = self.vertex_buffer
        p0 = vb.get_position(v0)
        p1 = vb.get_position(v1)
        p2 = vb.get_position(v2)

        epsilon = 0.0001
        minx = min(min(p0[0], p1[0]), p2[0]) - epsilon
        maxx = max(max(p0[0], p1[0]), p2[0]) + epsilon
        miny = min(min(p0[1], p1[1]), p2[1]) - epsilon
        maxy = max(max(p0[1], p1[1]), p2[1]) + epsilon
        minz = min(min(p0[2], p1[2]), p2[2]) - epsilon
        maxz = max(max(p0[2], p1[2]), p2[2]) + epsilon

        p0 = Vector3(minx, miny, minz)
        p1 = Vector3(maxx, maxy, maxz)
        return renmas.shapes.BBox(p0, p1, 99999) #material undefined #TODO fix BBox  implement Box

    def lst_triangles(self):
        lst = []
        for i in range(self.ntriangles()):
            v0, v1, v2 = self.triangles.get_vertices(i)
            vb = self.vertex_buffer
            p0 = vb.get_position(v0)
            p1 = vb.get_position(v1)
            p2 = vb.get_position(v2)
            ver0 = Vector3(p0[0], p0[1], p0[2])
            ver1 = Vector3(p1[0], p1[1], p1[2])
            ver2 = Vector3(p2[0], p2[1], p2[2])
            tri = renmas.shapes.Triangle(ver0, ver1, ver2, self.triangles.get_material(i)) 
            lst.append(tri)
        return lst

    def get_triangle(self, idx):
        v0, v1, v2 = self.triangles.get_vertices(idx)
        vb = self.vertex_buffer
        p0 = vb.get_position(v0)
        p1 = vb.get_position(v1)
        p2 = vb.get_position(v2)
        ver0 = Vector3(p0[0], p0[1], p0[2])
        ver1 = Vector3(p1[0], p1[1], p1[2])
        ver2 = Vector3(p2[0], p2[1], p2[2])
        tri = renmas.shapes.Triangle(ver0, ver1, ver2, self.triangles.get_material(idx)) 
        return tri

    def scale(self, xs, ys, zs):
        xs = float(xs)
        ys = float(ys)
        zs = float(zs)
        for i in range(self.vertex_buffer.nvertices()):
            px, py, pz = self.vertex_buffer.get_position(i)
            p0 = px * xs
            p1 = py * ys
            p2 = pz * zs
            self.vertex_buffer.edit_position(i, p0, p1, p2)

    def translate(self, xs, ys, zs):
        xs = float(xs)
        ys = float(ys)
        zs = float(zs)
        for i in range(self.vertex_buffer.nvertices()):
            px, py, pz = self.vertex_buffer.get_position(i)
            p0 = px + xs
            p1 = py + ys
            p2 = pz + zs
            self.vertex_buffer.edit_position(i, p0, p1, p2)

    def calculate_bbox(self):
        p0 = Vector3(9999999.0, 9999999.0, 9999999.0)
        p1 = Vector3(-9999999.0, -9999999.0, -9999999.0)
        self.bounding_box = renmas.shapes.BBox(p0, p1, None) 
        for i in range(self.ntriangles()):
            v0, v1, v2 = self.triangles.get_vertices(i)
            extend_bbox(self.vertex_buffer, v0, v1, v2, self.bounding_box)

    def isect(self, ray, min_dist = 999999.0):
        return self.grid.isect(ray, min_dist)

    def attributes(self):
        d = {}
        d["ptr_isect"] = self.ptr_isect 
        return d

    @classmethod
    def struct(cls):
        asm_code = """ #DATA
        """
        asm_code += util.structs("mesh3d") 
        asm_code += """
        #CODE
        #END
        """
        mc = util.get_asm().assemble(asm_code)
        return mc.get_struct("mesh3d")

    @classmethod
    def name(cls):
        return "mesh3d"

    @classmethod
    def isect_name(cls):
        return "ray_mesh3d_intersection"

    # eax = pointer to ray structure
    # ebx = pointer to mesh3d structure
    # ecx = pointer to minimum distance
    # edx = pointer to hitpoint
    @classmethod
    def isect_asm(self, runtime, label, populate=True):

        asm_structs = util.structs("ray", "mesh3d", "hitpoint")
        ASM = """
        #DATA
        """
        ASM += asm_structs + """
        #CODE
        """
        ASM += " global " + label + ":\n" + """
        ;we just use indirect call
        call dword [ebx + mesh3d.ptr_isect]
        ret
        """

        asm = util.get_asm()
        mc = asm.assemble(ASM, True)
        #mc.print_machine_code()
        name = "ray_mesh_intersection" + str(util.unique())
        runtime.load(name, mc)

    def prepare_isect_asm(self, runtime):
        asm_structs = util.structs("ray", "mesh3d", "hitpoint")
        
        ray_tri_name = "ray_mesh" + str(hash(self)) + str(util.unique())
        grid_mesh_name = "ray_gridmesh" + str(hash(self)) + str(util.unique())

        self._ray_tri_asm(runtime, ray_tri_name)
        self.grid.isect_asm(runtime, grid_mesh_name, ray_tri_name)

        ASM = """
        #DATA
        """
        ASM += asm_structs + """
        #CODE
        """
        ASM += "call " + grid_mesh_name + " \n"
        ASM += "ret \n "

        asm = util.get_asm()
        mc = asm.assemble(ASM, True)
        #mc.print_machine_code()
        name = "ray_mesh_intersection" + str(util.unique())
        runtime.load(name, mc)
        self.ptr_isect = runtime.address_module(name)

    def _ray_tri_asm(self, runtime, label):

        util.load_func(runtime, "ray_triangle_mesh")

        asm_structs = util.structs("ray", "hitpoint")

        ASM = """
        #DATA
        """
        ASM += asm_structs + """
        float min_dist = 999999.0
        float max_dist = 999999.0
        float zero = 0.0
        float one = 1.0
        float epsilon = 0.00001
        float minus_nesto = 0.0001

        ; pointer to vertex and triangle buffers
        uint32 vb_ptr
        uint32 tr_ptr
        uint32 vertices_size
        uint32 triangle_size

        #CODE
        """
        ASM += " global " + label + ":\n" + """
        ; eax - ray,  ebx - hp, ecx - min_dist, esi - ptr_arr, edi - nobj
        ; 64-bit version will bi i little different beacuse of different size of array
        macro eq32 min_dist = max_dist + one
        mov ecx, min_dist

        push ecx
        push eax
        push ebx
        push esi
        push edi
        mov edx, dword [minus_nesto]
        mov dword [ebx + hitpoint.t], edx

        _objects_loop:
        mov eax, dword [esp + 12] ; address of ray
        mov ecx, dword [esp + 16] ; address of minimum distance
        mov edx, dword [esp + 8]  ; address of hitpoint
        mov esi, dword [esp + 4] ; array of indexes of triangles 

        mov ebx, dword [esi]  ; put index of triangle in ebx

        ; prepeare call - address of  parameters
        ;addres of points, normal a value of material index
        ;addr = self.address.ptr() + index * self.tri_size 
        
        imul ebx, dword [triangle_size]
        add ebx, dword [tr_ptr]
        ; trbuffer tr_ptr=v0, tr_ptr+4=v1, tr_ptr+8=v2, tr_ptr+12=mat_idx , tr_ptr+16=normal
        mov ebp, dword [ebx + 12]
        push ebp

        mov ebp, ebx
        add ebp, 16
        push ebp

        mov ebp, dword [ebx + 8] 
        imul ebp, dword [vertices_size]
        add ebp, dword [vb_ptr]
        push ebp
        
        mov ebp, dword [ebx + 4] 
        imul ebp, dword [vertices_size]
        add ebp, dword [vb_ptr]
        push ebp
        mov ebp, dword [ebx] 
        imul ebp, dword [vertices_size]
        add ebp, dword [vb_ptr]
        push ebp
        
        call ray_triangle_mesh
        add esp, 20

        cmp eax, 0  ; 0 - no intersection ocur 1 - intersection ocur
        jne _update_distance
        _next_object:
        sub dword [esp], 1  
        jz _end_objects
        add dword [esp + 4], 4  ;increment array by 4 - index of triangle
        jmp _objects_loop


        _update_distance:
        mov eax, dword [esp + 8]
        mov ebx, dword [eax + hitpoint.t]

        mov edx, dword [esp + 16] ;populate new minimum distance
        mov dword [edx], ebx
        jmp _next_object
        
        _end_objects:
        add esp, 20 
        macro eq32 xmm0 = min_dist
        macro if xmm0 < max_dist goto _accept
        mov eax, 0
        ret

        _accept:
        macro if xmm0 < epsilon goto _reject
        mov eax, 1
        ret

        _reject:
        mov eax, 0
        ret

        """

        asm = util.get_asm()
        mc = asm.assemble(ASM, True)
        #mc.print_machine_code()
        name = "ray_tri_intersection" + str(util.unique())
        self.ds = runtime.load(name, mc)

        self.ds['vertices_size'] = self.vertex_buffer.vsize() 
        self.ds['triangle_size'] = self.triangles.tsize()
        self.ds['vb_ptr'] = self.vertex_buffer.addr()
        self.ds['tr_ptr'] = self.triangles.addr()


    def ray_tri(self, ray, idx, min_dist = 999999.0):
        v0, v1, v2 = self.triangles.get_vertices(idx)
        vb = self.vertex_buffer
        p0 = vb.get_position(v0)
        p1 = vb.get_position(v1)
        p2 = vb.get_position(v2)

        a = p0[0] - p1[0]
        b = p0[0] - p2[0] 
        c = ray.dir.x
        d = p0[0] - ray.origin.x
        e = p0[1] - p1[1]
        f = p0[1] - p2[1]
        g = ray.dir.y
        h = p0[1] - ray.origin.y
        i = p0[2] - p1[2] 
        j = p0[2] - p2[2]
        k = ray.dir.z
        l = p0[2] - ray.origin.z

        m = f * k - g * j
        n = h * k - g * l
        p = f * l - h * j
        q = g * i - e * k
        s = e * j - f * i

        temp3 =  (a * m + b * q + c * s)
        if temp3 == 0.0: return False
        inv_denom = 1.0 / temp3

        e1 = d * m - b * n - c * p
        beta = e1 * inv_denom

        if beta < 0.0: return False

        r = e * l - h * i
        e2 = a * n + d * q + c * r
        gamma = e2 * inv_denom

        if gamma < 0.0: return False

        if beta + gamma > 1.0: return False

        e3 = a * p - b * r + d * s
        t = e3 * inv_denom

        if t < 0.00001: return False # self-intersection

        hit_point = ray.origin + ray.dir * t

        temp = self.triangles.get_normal(idx)
        normal = Vector3(temp[0], temp[1], temp[2])
        return renmas.shapes.HitPoint(t, hit_point, normal, self.triangles.get_material(idx), ray)

    

import struct
from .buffers import VertexBuffer, VertexNBuffer, TriangleBuffer, TriangleNBuffer

class Ply:
    def __init__(self):
        self.format = None # ascii , binary big endian or little endian
        self.version = None
        self.name = None
        self._lst_elements = []
        self._properties = {}
        self._vertex_buffer = None
        self._triangle_buffer = None

    @property
    def vertex_buffer(self):
        return self._vertex_buffer

    @property
    def triangle_buffer(self):
        return self._triangle_buffer

    def _read_bin_to_asci_line(self, f):
        a = b''
        for i in range(5000):
            c = f.read(1)
            d = str(c, "ascii")
            if d =='\r' or d == "\n":
                break
            a += c 
        return str(a, "ascii") 

    def show_header(self):
        if self.name is None: return
        s = "%s %s %s" %(self.name, self.format, self.version)
        print(s)
        for e in self._lst_elements:
            print(e[0], e[1])
            props = self._properties[e]
            for p in props:
                print(p)

    def _read_header(self, readline):
        while True:
            line = readline()
            words = line.split()
            #ignore empty lines and comments and finish header on end_header keyword
            if len(words) == 0: continue
            if words[0] == "comment": continue
            if words[0] == "end_header": break
            if words[0] == "format":
                if words[1] == "ascii": 
                    self.format = "ASCII"
                elif words[1] == "binary_big_endian":
                    self.format = "BE"
                elif words[1] == "binary_little_endian":
                    self.format = "LE"
                self.version = words[2]
            elif words[0] == "element":
                element = (words[1], int(words[2]))
                self._lst_elements.append(element)
                self._properties[element] = []
            elif words[0] == "property":
                if words[1] == "list":
                    prop = (words[2], words[3], words[4])
                else:
                    prop = (words[1], words[2])
                self._properties[self._lst_elements[-1]].append(prop)

    def _read_ascii_vt(self, nvertex, f, idx_u, idx_v):
        raise ValueError("Not yet implemented")
    
    def _read_ascii_vtn(self, nvertex, f, idx_nx, idx_ny, idx_nz, idx_u, idx_v):
        raise ValueError("Not yet implemented")

    def _read_ascii_vn(self, nvertex, f, idx_nx, idx_ny, idx_nz):
        self._vertex_buffer = vb = VertexNBuffer(nvertex) 
        num = 0 #number of vertices read
        for line in f:
            words = line.split()
            if len(words) == 0: continue
            x = float(words[0])
            y = float(words[1])
            z = float(words[2])
            nx = float(words[idx_nx])
            ny = float(words[idx_ny])
            nz = float(words[idx_nz])
            vb.add(x, y, z, nx, ny, nz)
            num += 1
            if num == nvertex: break # we finish read all vertices

    def _read_ascii_v(self, nvertex, f):
        self._vertex_buffer = vb = VertexBuffer(nvertex) 
        num = 0 #number of vertices read
        for line in f:
            words = line.split()
            if len(words) == 0: continue
            x = float(words[0])
            y = float(words[1])
            z = float(words[2])
            vb.add(x, y, z)
            num += 1
            if num == nvertex: break # we finish read all vertices

    def _read_ascii_vertices(self, element, f):
        name, nvertex = element
        if name != "vertex":
            raise ValueError("Unknow element, expected element vertex but got " + name)
        props = self._properties[element]
        idx_nx = idx_ny = idx_nz = idx_u = idx_v = None
        for i in range(len(props)):
            typ, name = props[i]
            if name == "nx": idx_nx = i
            if name == "ny": idx_ny = i
            if name == "nz": idx_nz = i
            if name == "u": idx_u = i
            if name == "v": idx_u = i
        if idx_nx is None or idx_ny is None or idx_nz is None:
            if idx_u is None or idx_v is None:
                self._read_ascii_v(nvertex, f)
            else:
                self._read_ascii_vt(nvertex, f, idx_u, idx_v)
        else:
            if idx_u is None or idx_v is None:
                self._read_ascii_vn(nvertex, f, idx_nx, idx_ny, idx_nz)
            else:
                self._read_ascii_vtn(nvertex, f, idx_nx, idx_ny, idx_nz, idx_u, idx_v)

    def _size_format(self, typ):
        if typ == "char":
            size = 1
            format_line = "c"
        elif typ == "uchar": 
            size = 1
            format_line = "B"
        elif typ == "short":
            size = 2 
            format_line = "h"
        elif typ == "ushort": 
            size = 2 
            format_line = "H"
        elif typ == "int":
            size = 4 
            format_line = "i"
        elif typ == "uint": 
            size = 4 
            format_line = "I"
        elif typ == "float": 
            size = 4
            format_line = "f"
        elif typ == "double":
            size = 8
            format_line = "d"
        else:
            raise ValueError("Unknow type " + typ)
        return (size, format_line)

    def _read_binary_vertices(self, element, f):
        name, nvertex = element
        if name != "vertex":
            raise ValueError("Unknow element, expected element vertex but got " + name)
        props = self._properties[element]
        idx_nx = idx_ny = idx_nz = idx_u = idx_v = None
        item_size = 0
        format_line = ""
        for i in range(len(props)):
            typ, name = props[i]
            if name == "nx": idx_nx = i
            if name == "ny": idx_ny = i
            if name == "nz": idx_nz = i
            if name == "u": idx_u = i
            if name == "v": idx_u = i
            size, flag = self._size_format(typ)
            item_size += size
            format_line += flag

        if self.format == "BE":
            format_line = ">" + format_line
        else:
            format_line = "<" + format_line

        if idx_nx is None or idx_ny is None or idx_nz is None:
            if idx_u is None or idx_v is None:
                self._vertex_buffer = vb = VertexBuffer(nvertex) 
                for i in range(nvertex):
                    buff = f.read(item_size)
                    v = struct.unpack(format_line, buff) #first three numbers are x, y, z
                    vb.add(v[0], v[1], v[2])
            else:
                raise ValueError("Not yet implemented")
        else:
            if idx_u is None or idx_v is None:
                self._vertex_buffer = vb = VertexNBuffer(nvertex) 
                for i in range(nvertex):
                    buff = f.read(item_size)
                    v = struct.unpack(format_line, buff) #first three numbers are x, y, z
                    vb.add(v[0], v[1], v[2], v[idx_nx], v[idx_ny], v[idx_nz])
            else:
                raise ValueError("Not yet implemented")

    def _read_ascii_faces(self, element, f):
        name, nfaces = element
        if name != "face":
            raise ValueError("Unknow element, expected element face but got " + name)
        props = self._properties[element]
        self._triangle_buffer = tb = TriangleBuffer(nfaces)
        num = 0 #number of faces read
        for line in f:
            words = line.split()
            if len(words) == 0: continue
            nindices = int(words[0])
            for f in range(2,nindices):
                idx1 = int(words[1])
                idx2 = int(words[f])
                idx3 = int(words[f+1])
                tb.add(idx1,idx2,idx3)
            num += 1
            if num == nfaces: break # we finish read all vertices

    def _read_binary_faces(self, element, f):
        name, nfaces = element
        if name != "face":
            raise ValueError("Unknow element, expected element face but got " + name)
        props = self._properties[element]
        rest_size = 0

        for i in range(len(props)):
            if len(props[i]) == 2:
                typ, name = props[i]
                size, flag = self._size_format(typ)
                rest_size += size
        if self.format == "BE":
            endian = ">" 
        else:
            endian = "<"

        typ1, typ2, name = props[0] #list property
        size1, flag1 = self._size_format(typ1)
        size2, flag2 = self._size_format(typ2)
        format_line1 = endian + flag1
        format_line2 = endian + flag2 + flag2 + flag2
        format_line3 = endian + flag2 + flag2 + flag2 + flag2
        sz2 = size2 * 3
        sz3 = size2 * 4
        
        self._triangle_buffer = tb = TriangleBuffer(nfaces)
        for i in range(nfaces):
            buff = f.read(size1)
            n = struct.unpack(format_line1, buff)[0]
            if n == 3:
                buff = f.read(sz2)
                t = struct.unpack(format_line2, buff)
                tb.add(t[0], t[1], t[2])
            elif n == 4:
                buff = f.read(sz3)
                t = struct.unpack(format_line3, buff)
                tb.add(t[0], t[1], t[2])
                tb.add(t[0], t[2], t[3])
            else:
                raise ValueError("List is two long " + str(n))
            if rest_size != 0:
                buff = f.read(rest_size)

    def _detect_format(self, fname):
        f = open(fname, "rb")
        while True:
            line = self._read_bin_to_asci_line(f)
            words = line.split()
            if len(words) == 0: continue
            if words[0] == "comment": continue
            if words[0] == "end_header": break
            if words[0] == "format":
                if words[1] == "ascii": 
                    self.format = "ASCII"
                elif words[1] == "binary_big_endian":
                    self.format = "BE"
                elif words[1] == "binary_little_endian":
                    self.format = "LE"
                self.version = words[2]
                break
        f.close()


    def load(self, fname):
        self._detect_format(fname)
        if self.format == "ASCII":
            f = open(fname)
            self.name = fname
            self._read_header(f.readline)

            # 1 element is vertices list
            element = self._lst_elements[0]
            self._read_ascii_vertices(element, f)
            # 2 element is faces list
            element = self._lst_elements[1]
            self._read_ascii_faces(element, f)

            f.close()

        else:
            f = open(fname, "rb")
            self.name = fname
            self._read_header(lambda : self._read_bin_to_asci_line(f))
            element = self._lst_elements[0]
            self._read_binary_vertices(element, f)

            element = self._lst_elements[1]
            self._read_binary_faces(element, f)

            f.close()




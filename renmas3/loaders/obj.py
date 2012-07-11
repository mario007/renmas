
import os
import os.path
from ..core import VertexBuffer, VertexNBuffer, VertexUVBuffer, VertexNUVBuffer, TriangleBuffer
from ..shapes import MeshDesc

class Obj:
    def __init__(self):
        pass
        
    def check_seq(self, seq1, seq2):
        if len(seq1) != len(seq2):
            return False
        for i in range(len(seq1)):
            if seq1[i] != seq2[i]: 
                return False 
        return True

    def _group(self, words):
        if len(words) == 1: 
            self._current_groups = ["default" + str(len(self._vertices))]  
            self._new_groups = True
        else:
            if not self.check_seq(self._current_groups, words[1:]):
                self._current_groups = words[1:]
                self._new_groups = True

    def _usemtl(self, words):
        if len(words) > 1:
            self._current_material = words[1]

    def _face(self, words):
        face = []
        texco = []
        norms = []
        for v in words[1:]:
            w = v.split('/')
            face.append(int(w[0]))
            if len(w) > 1 and w[1] != "":
                texco.append(int(w[1]))
            if len(w) > 2:
                norms.append(int(w[2]))

        #split face on triangles 
        for idx in range(len(face[2:])):
            v0 = face[0]
            v1 = face[idx+1]
            v2 = face[idx+2]
            t0=t1=t2=n0=n1=n2=None
            if len(texco) > 0:
                t0 = texco[0]
                t1 = texco[idx+1]
                t2 = texco[idx+2]
            if len(norms) > 0:
                n0 = norms[0]
                n1 = norms[idx+1]
                n2 = norms[idx+2]

            #build new vertex list and index list of triangles
            v0 = self._get_vertex(v0, t0, n0)
            v1 = self._get_vertex(v1, t1, n1)
            v2 = self._get_vertex(v2, t2, n2)
            self._current_tb.add(v0, v1, v2)

    def _set_defaults(self):
        self._shape_names = {}
        self._vertex_idx = {} 
        self._meshs = []
        self._normals =  VertexBuffer()
        self._normals.add(0.0, 0.0, 1.0) # dummy value - index starts at 1
        self._uv = [(0.0,0.0)] # dummy value - index starts at 1
        
        self._vertices =  VertexBuffer()
        self._vertices.add(0.0, 0.0, 0.0) # dummy value - index starts at 1

        self._current_groups = ["default"]
        self._new_groups = True
        self._current_material = "default"

    def load(self, fname):
        if not os.path.isfile(fname): return None #file doesn't exists

        self._set_defaults()

        f = open(fname, "r")
        for line in f:
            line = line.strip()
            if line == "": continue # skip blank lines
            words = line.split()
            if words[0][0] == "#": continue # skip comments
            if words[0] == "v":
                self._vertices.add(float(words[1]), float(words[2]), float(words[3]))
            elif words[0] == "vn":
                self._normals.add(float(words[1]), float(words[2]), float(words[3]))
            elif words[0] == "vt":
                self._uv.append((float(words[1]), float(words[2])))
            elif words[0] == "g":
                self._group(words)
            elif words[0] == "usemtl":
                self._usemtl(words)
            elif words[0] == 'f': #index in previos arrays
                self._face(words)
        
        self._vertices.clear()
        self._normals.clear()
        #self._uv = self._vertex_idx = None 
        self._vertex_idx = None
        f.close()
        return tuple(self._meshs)

    def _get_vertex(self, v, t, n):
        if self._new_groups:
            self._create_buffers(t, n)
            self._vertex_idx = {} 
            self._new_groups = None

        if (v, t, n) in self._vertex_idx:
            return self._vertex_idx[(v,t,n)]
        else: #if vertex doesn't exist we must create new one
            if v < 0:
                x, y, z = self._vertices.get(self._vertices.size() - abs(v))
            else:
                x, y, z = self._vertices.get(v)
            idx = self._current_vb.size()
            if t is None and n is None: self._current_vb.add(x, y, z)
            elif t is None and n is not None: 
                if n < 0:
                    nx, ny, nz = self._normals.get(self._normals.size() - abs(n))
                else:
                    nx, ny, nz = self._normals.get(n)
                self._current_vb.add(x, y, z, nx, ny, nz)
            elif t is not None and n is None:
                u1, v1 = self._uv[t]
                self._current_vb.add(x, y, z, u1, v1)
            else:
                if n < 0:
                    nx, ny, nz = self._normals.get(self._normals.size() - abs(n))
                else:
                    nx, ny, nz = self._normals.get(n)
                u1, v1 = self._uv[t]
                self._current_vb.add(x, y, z, nx, ny, nz, u1, v1)

            self._vertex_idx[(v,t,n)] = idx
            if len(self._vertex_idx) > 2000000: self._vertex_idx.clear()
            return idx

    def _create_buffers(self, texture=None, normals=None):
        if texture is None and normals is None:
            vb = VertexBuffer()
        elif texture is None and normals is not None:
            vb = VertexNBuffer()
        elif texture is not None and normals is None:
            vb = VertexUVBuffer()
        else:
            vb = VertexNUVBuffer()
        self._current_vb = vb
        self._current_tb = tb = TriangleBuffer()


        buffname = "_".join(self._current_groups)
        if buffname in self._shape_names:
            buffname += str(hash(self))
        self._shape_names[buffname] = buffname
        
        buff = MeshDesc(vb, tb, buffname, self._current_material)
        self._meshs.append(buff)
        


import os
import os.path
from .buffers import VertexBuffer, VertexNBuffer, VertexUVBuffer, VertexNUVBuffer, TriangleBuffer

class MeshBuff:
    def __init__(self, vb, tb, name, material):
        self.vb = vb
        self.tb = tb
        self.name = name
        self.mat_name = material

class Obj:
    def __init__(self):
        #output meshes 
        self._meshs = []
        
        #temp containers
        self._vertices = []
        self._normals = []
        self._uv = []
        self._vertex_idx = {} 

    @property
    def meshes(self):
        return self._meshs

    def check_seq(self, seq1, seq2):
        if len(seq1) != len(seq2):
            return False
        for i in range(len(seq1)):
            if seq1[i] != seq2[i]: 
                return False 
        return True

    def load(self, fname):
        if not os.path.exists(fname): return False
        self._shape_names = {}

        self._meshs = []
        self._vertices = [(0.0,0.0,0.0)] # dummy value - index starts at 1
        self._normals = [(0.0,0.0,1.0)] # dummy value - intex starts at 1
        self._uv = [(0.0,0.0)] # dummy value - index starts at 1
        
        self._current_groups = ["default"]
        self._new_groups = True
        self._current_material = "default"

        f = open(fname, "r")
        for line in f:
            line = line.strip()
            if line == "": continue # skip blank lines
            words = line.split()
            if words[0][0] == "#": continue # skip comments
            if words[0] == "v":
                self._vertices.append((float(words[1]), float(words[2]), float(words[3])))
            elif words[0] == "vn":
                self._normals.append((float(words[1]), float(words[2]), float(words[3])))
            elif words[0] == "vt":
                try:
                    a, b = float(words[1]), float(words[2])
                except:
                    print(words)
                self._uv.append((float(words[1]), float(words[2])))
            elif words[0] == "g":
                if len(words) == 1: 
                    self._current_groups = ["default" + str(len(self._vertices))]  
                    self._new_groups = True
                else:
                    if not self.check_seq(self._current_groups, words[1:]):
                        self._current_groups = words[1:]
                        self._new_groups = True
            elif words[0] == "usemtl":
                if len(words) > 1:
                    self._current_material = words[1]

            elif words[0] == 'f': #index in previos arrays
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
                    
        
        self._vertices = self._normals = self._uv = self._vertex_idx = None 
        f.close()
        return True

    def _get_vertex(self, v, t, n):
        if self._new_groups:
            self._create_buffers(t, n)
            self._vertex_idx = {} 
            self._new_groups = None
        if t is None and n is None:
            if v in self._vertex_idx:
                return self._vertex_idx[v]
            else:
                x, y, z = self._vertices[v]
                idx = self._current_vb.size()
                self._current_vb.add(x, y, z)
                self._vertex_idx[v] = idx
                return idx
        elif t is None and n is not None:
            if (v,n) in self._vertex_idx:
                return self._vertex_idx[(v,n)]
            else:
                x, y, z = self._vertices[v]
                nx, ny, nz = self._normals[n]
                idx = self._current_vb.size()
                self._current_vb.add(x, y, z, nx, ny, nz)
                self._vertex_idx[(v,n)] = idx
                return idx
        elif t is not None and n is None:
            if (v,t) in self._vertex_idx:
                return self._vertex_idx[(v,t)]
            else:
                x, y, z = self._vertices[v]
                u1, v1 = self._uv[t]
                idx = self._current_vb.size()
                self._current_vb.add(x, y, z, u1, v1)
                self._vertex_idx[(v,t)] = idx
                return idx
        else:
            if (v,t,n) in self._vertex_idx:
                return self._vertex_idx[(v,t,n)]
            else:
                x, y, z = self._vertices[v]
                nx, ny, nz = self._normals[n]
                u1, v1 = self._uv[t]
                idx = self._current_vb.size()
                self._current_vb.add(x, y, z, nx, ny, nz, u1, v1)
                self._vertex_idx[(v,t,n)] = idx
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

        buff = MeshBuff(vb, tb, buffname, self._current_material)
        self._meshs.append(buff)
        

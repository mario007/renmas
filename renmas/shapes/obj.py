import os
import os.path

class OBJ:
    def __init__(self):

        self.vertex = [] #has all, position, texture, normals
        self.triangles = []
        self.has_normal = False
        self.has_texcoords = False

        #be cerfull about grouping and other stuff!!!
        #if we have more than one object in file
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.vertex_idx = {} 

    def load(self, filename):
        if not os.path.exists(filename): return False
        self.has_normal = False
        self.has_texcoords = False

        self.vertices.append((0.0, 0.0, 0.0)) #dummy value - index starts ad 1
        self.normals.append((0.0, 0.0, 0.0)) #dummy value - index starts ad 1
        self.texcoords.append((0.0, 0.0)) #dummy value - index starts ad 1

        f = open(filename, "r")
        lines = f.readlines()
        for line in lines:
            values = line.split()
            if len(values) < 1: continue
            if values[0] == '#': continue
            if values[0] == 'v':
                x = float(values[1])
                y = float(values[2])
                z = float(values[3])
                self.vertices.append((x,y,z))
            elif values[0] == 'vn':
                x = float(values[1])
                y = float(values[2])
                z = float(values[3])
                self.has_normal = True
                self.normals.append((x,y,z))
            elif values[0] == 'vt':
                s = float(values[1])
                t = float(values[2])
                self.has_texcoords = True
                self.texcoords.append((s,t))
            elif values[0] == 'f': #index in previos arrays
                face = []
                texco = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        texco.append(int(w[1]))
                    else:
                        self.has_texcoords = False 
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        self.has_normal = False 

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
                    
                    # build new vertex list and index list of triangles
                    vertex1 = self.build_vertex(v0, t0, n0)
                    vertex2 = self.build_vertex(v1, t1, n1)
                    vertex3 = self.build_vertex(v2, t2, n2)
                    self.triangles.append((vertex1, vertex2, vertex3))

        
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.vertex_idx = {} 
        return True

    def build_vertex(self, v, t, n):

        if self.has_normal and self.has_texcoords:
            if (v,t,n) in self.vertex_idx:
                return self.vertex_idx[(v,t,n)]
            else:
                x, y, z = self.vertices[v]
                nx, ny, nz = self.normals[n]
                u1, v1 = self.texcoords[t]
                idx = len(self.vertex)
                self.vertex.append((x, y, z, nx, ny, nz, u1, v1))
                self.vertex_idx[(v,t,n)] = idx
                return idx
        elif self.has_normal:
            if (v,n) in self.vertex_idx:
                return self.vertex_idx[(v,n)]
            else:
                x, y, z = self.vertices[v]
                nx, ny, nz = self.normals[n]
                idx = len(self.vertex)
                self.vertex.append((x, y, z, nx, ny, nz))
                self.vertex_idx[(v,n)] = idx
                return idx
        elif self.has_texcoords:
            if (v,t) in self.vertex_idx:
                return self.vertex_idx[(v,t)]
            else:
                x, y, z = self.vertices[v]
                u1, v1 = self.texcoords[t]
                idx = len(self.vertex)
                self.vertex.append((x, y, z, u1, v1))
                self.vertex_idx[(v,t)] = idx
                return idx
        else:#we have just position
            if v in self.vertex_idx:
                return self.vertex_idx[v]
            else:
                x, y, z = self.vertices[v]
                idx = len(self.vertex)
                self.vertex.append((x, y, z))
                self.vertex_idx[v] = idx
                return idx



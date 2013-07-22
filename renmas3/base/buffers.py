
import x86
from tdasm import Tdasm, Runtime
from .memcopy import memcpy

class Buffer:
    def __init__(self, item_size, reserve=0):
        self._reserve = reserve
        self._item_size = item_size
        self._size = 0

        if self._reserve > 0:
            self._address = x86.MemData(self._reserve*self._item_size)
        else:
            self._address = None

    def item_size(self):
        return self._item_size

    def size(self):
        return self._size

    def clear(self):
        self._address = None
        self._size = 0
        self._reserve = 0

    def addr(self):
        if self._address:
            return self._address.ptr()  
        return None

    def _resize(self):
        if self._size >= 0 and self._size <= 100:
            self._reserve += 1
        elif self._size > 100 and self._size <= 10000:
            self._reserve += 100
        elif self._size > 10000 and self._size <= 1000000:
            self._reserve += 10000
        else:
            self._reserve += 100000

        temp = x86.MemData(self._item_size*self._reserve)
        if self._address:
            memcpy(temp.ptr(), self._address.ptr(), self._size*self._item_size) 
        self._address = temp

class Vertices(Buffer):
    def __init__(self, vertex_size, reserve=0):
        super(Vertices, self).__init__(vertex_size, reserve)

    def scale(self, xs, ys, zs):
        xs = float(xs)
        ys = float(ys)
        zs = float(zs)
        addr = self._address.ptr()
        for i in range(self._size):
            p = x86.GetFloat(addr, 0, 3)
            v0 = xs * p[0]
            v1 = ys * p[1]
            v2 = zs * p[2]
            x86.SetFloat(addr, (v0, v1, v2, 0.0), 0)
            addr += self._item_size

    def translate(self, dx, dy, dz):
        dx = float(dx)
        dy = float(dy)
        dz = float(dz)
        addr = self._address.ptr()
        for i in range(self._size):
            p = x86.GetFloat(addr, 0, 3)
            v0 = dx + p[0]
            v1 = dy + p[1]
            v2 = dz + p[2]
            x86.SetFloat(addr, (v0, v1, v2, 0.0), 0)
            addr += self._item_size

    def bbox_triangle(self, idx1, idx2, idx3):
        address = self._address.ptr()
        addr = address + idx1 * self._item_size 
        p0 = x86.GetFloat(addr, 0, 3)
        addr = address + idx2 * self._item_size 
        p1 = x86.GetFloat(addr, 0, 3)
        addr = address + idx3 * self._item_size 
        p2 = x86.GetFloat(addr, 0, 3)
        epsilon = 0.0001
        minx = p0[0]
        if p1[0] < minx: minx = p1[0]
        if p2[0] < minx: minx = p2[0]
        minx -= epsilon
        maxx = p0[0]
        if p1[0] > maxx: maxx = p1[0]
        if p2[0] > maxx: maxx = p2[0]
        maxx += epsilon
        miny = p0[1]
        if p1[1] < miny: miny = p1[1]
        if p2[1] < miny: miny = p2[1]
        miny -= epsilon
        maxy = p0[1]
        if p1[1] > maxy: maxy = p1[1]
        if p2[1] > maxy: maxy = p2[1]
        maxy += epsilon
        minz = p0[2]
        if p1[2] < minz: minz = p1[2]
        if p2[2] < minz: minz = p2[2]
        minz -= epsilon
        maxz = p0[2]
        if p1[2] > maxz: maxz = p1[2]
        if p2[2] > maxz: maxz = p2[2]
        maxz += epsilon
        #minx = min(min(p0[0], p1[0]), p2[0]) - epsilon
        #maxx = max(max(p0[0], p1[0]), p2[0]) + epsilon
        #miny = min(min(p0[1], p1[1]), p2[1]) - epsilon
        #maxy = max(max(p0[1], p1[1]), p2[1]) + epsilon
        #minz = min(min(p0[2], p1[2]), p2[2]) - epsilon
        #maxz = max(max(p0[2], p1[2]), p2[2]) + epsilon
        return((minx, miny, minz), (maxx, maxy, maxz))

    #TODO --- asm version of this method is required!!! lucy is slow??
    #TODO --- make adaptive epsilon - depend how big values are in the buffer
    def bbox(self):
        if self.addr():
            minx = miny = minz = 9999999.0
            maxx = maxy = maxz = -9999999.0
            epsilon = 0.001
            addr = self._address.ptr()

            for i in range(self._size):
                p = x86.GetFloat(addr, 0, 3)
                if p[0] < minx: minx = p[0]
                if p[1] < miny: miny = p[1]
                if p[2] < minz: minz = p[2]
                if p[0] > maxx: maxx = p[0]
                if p[1] > maxy: maxy = p[1]
                if p[2] > maxz: maxz = p[2]
                addr += self._item_size
            
            minx = minx - epsilon
            miny = miny - epsilon
            minz = minz - epsilon
            maxx = maxx + epsilon
            maxy = maxy + epsilon
            maxz = maxz + epsilon
            return((minx, miny, minz), (maxx, maxy, maxz))
        return None

# Buffer that store x,y,z cordinnates of vertex 
class VertexBuffer(Vertices):
    def __init__(self, reserve=0):
        super(VertexBuffer, self).__init__(16, reserve)

    def add(self, x, y, z):
        if self._reserve == self._size:
            self._resize()
        offset = self._item_size * self._size
        x86.SetFloat(self._address.ptr()+offset, (x, y, z, 0.0), 0)
        self._size += 1

    def edit(self, index, x, y, z):
        if index < self._size:
            addr = self._address.ptr() + index * self._item_size 
            x86.SetFloat(addr, (x, y, z, 0.0), 0)
        #think throwing exception TODO

    def get(self, index):
        if index < self._size:
            addr = self._address.ptr() + index * self._item_size 
            return x86.GetFloat(addr, 0, 3)
        return None #think Trowing exception TODO


#Buffer that stores x,y,z and normal(nx,ny,nz) of vertex
class VertexNBuffer(Vertices):
    def __init__(self, reserve=0):
        super(VertexNBuffer, self).__init__(32, reserve)

    def add(self, x, y, z, nx, ny, nz):
        if self._reserve == self._size:
            self._resize()

        offset = self._item_size * self._size
        x86.SetFloat(self._address.ptr()+offset, (x, y, z, 0.0), 0)
        x86.SetFloat(self._address.ptr()+offset+16, (nx, ny, nz, 0.0), 0)
        self._size += 1

    def edit(self, index, x, y, z, nx, ny, nz):
        if index < self._size:
            addr = self._address.ptr() + index * self._item_size 
            x86.SetFloat(addr, (x, y, z, 0.0), 0)
            x86.SetFloat(addr+16, (nx, ny, nz, 0.0), 0)
        #think throwing exception TODO

    def get(self, index):
        if index < self._size:
            addr = self._address.ptr() + index * self._item_size 
            p = x86.GetFloat(addr, 0, 3)
            n = x86.GetFloat(addr+16, 0, 3)
            return(p,n)
        return None #think Trowing exception TODO

#Buffer that stores x,y,z and u,v for texturing
class VertexUVBuffer(Vertices):
    def __init__(self, reserve=0):
        super(VertexUVBuffer, self).__init__(32, reserve)

    def add(self, x, y, z, u, v):
        if self._reserve == self._size:
            self._resize()

        offset = self._item_size * self._size
        x86.SetFloat(self._address.ptr()+offset, (x, y, z, 0.0), 0)
        x86.SetFloat(self._address.ptr()+offset+16, (u, v, 0.0, 0.0), 0)
        self._size += 1

    def edit(self, index, x, y, z, u, v):
        if index < self._size:
            addr = self._address.ptr() + index * self._item_size 
            x86.SetFloat(addr, (x, y, z, 0.0), 0)
            x86.SetFloat(addr+16, (u, v, 0.0, 0.0), 0)
        #think throwing exception TODO

    def get(self, index):
        if index < self._size:
            addr = self._address.ptr() + index * self._item_size 
            p = x86.GetFloat(addr, 0, 3)
            uv = x86.GetFloat(addr+16, 0, 2)
            return(p,uv)
        return None #think Trowing exception TODO


#Buffer that stores x,y,z and normal(nx,ny,nz) of vertex, and also u,v for texturing
class VertexNUVBuffer(Vertices):
    def __init__(self, reserve=0):
        super(VertexNUVBuffer, self).__init__(48, reserve)

    def add(self, x, y, z, nx, ny, nz, u, v):
        if self._reserve == self._size:
            self._resize()

        offset = self._item_size * self._size
        x86.SetFloat(self._address.ptr()+offset, (x, y, z, 0.0), 0)
        x86.SetFloat(self._address.ptr()+offset+16, (nx, ny, nz, 0.0), 0)
        x86.SetFloat(self._address.ptr()+offset+32, (u, v, 0.0, 0.0), 0)
        self._size += 1

    def edit(self, index, x, y, z, nx, ny, nz, u, v):
        if index < self._size:
            addr = self._address.ptr() + index * self._item_size 
            x86.SetFloat(addr, (x, y, z, 0.0), 0)
            x86.SetFloat(addr+16, (nx, ny, nz, 0.0), 0)
            x86.SetFloat(addr+32, (u, v, 0.0, 0.0), 0)
        #think throwing exception TODO

    def get(self, index):
        if index < self._size:
            addr = self._address.ptr() + index * self._item_size 
            p = x86.GetFloat(addr, 0, 3)
            n = x86.GetFloat(addr+16, 0, 3)
            uv = x86.GetFloat(addr+32, 0, 2)
            return(p,n,uv)
        return None #think Trowing exception TODO


#Buffer that stores 3 triangle indexes in vertex buffer v0, v1, v2
class TriangleBuffer(Buffer):
    def __init__(self, reserve=0):
            super(TriangleBuffer, self).__init__(12, reserve)

    def add(self, v0, v1, v2):
        if self._reserve == self._size:
            self._resize()

        offset = self._item_size * self._size
        x86.SetUInt32(self._address.ptr()+offset, (v0,v1,v2), 0)
        self._size += 1

    def edit(self, index, v0, v1, v2):
        if index < self._size:
            addr = self._address.ptr() + index * self._item_size 
            x86.SetUInt32(addr, (v0, v1, v2), 0)

    def get(self, index):
        if index < self._size:
            addr = self._address.ptr() + index * self._item_size 
            return x86.GetUInt32(addr, 0, 3)
        return None

#Buffer that stores 3 triangle indexes in vertex buffer v0, v1, v2 and normal(nx,ny,nz)
class TriangleNBuffer(Buffer):
    def __init__(self, reserve=0):
            super(TriangleNBuffer, self).__init__(32, reserve)

    def add(self, v0, v1, v2, nx, ny, nz):
        if self._reserve == self._size:
            self._resize()

        offset = self._item_size * self._size
        addr = self._address.ptr()+offset
        x86.SetUInt32(addr, (v0,v1,v2), 0)
        x86.SetFloat(addr+16, (nx, ny, nz, 0.0), 0)
        self._size += 1

    def edit(self, index, v0, v1, v2, nx, ny, nz):
        if index < self._size:
            addr = self._address.ptr() + index * self._item_size 
            x86.SetUInt32(addr, (v0, v1, v2), 0)
            x86.SetFloat(addr+16, (nx, ny, nz, 0.0), 0)

    def get(self, index):
        if index < self._size:
            addr = self._address.ptr() + index * self._item_size 
            p = x86.GetUInt32(addr, 0, 3)
            n = x86.GetFloat(addr+16, 0, 3)
            return(p,n)
        return None

#Buffer that stores 3 triangle points 
class FlatTriangleBuffer(Buffer):
    def __init__(self, reserve=0):
            super(FlatTriangleBuffer, self).__init__(48, reserve) #TODO try performanse with 64 bytes

    def add(self, p0, p1, p2):
        if self._reserve == self._size:
            self._resize()

        offset = self._item_size * self._size
        addr = self._address.ptr()+offset
        x86.SetFloat(addr, (p0[0], p0[1], p0[2], 0.0), 0)
        x86.SetFloat(addr+16, (p1[0], p1[1], p1[2], 0.0), 0)
        x86.SetFloat(addr+32, (p2[0], p2[1], p2[2], 0.0), 0)
        self._size += 1

    def edit(self, index, p0, p1, p2):
        if index < self._size:
            addr = self._address.ptr() + index * self._item_size 
            x86.SetFloat(addr, (p0[0], p0[1], p0[2], 0.0), 0)
            x86.SetFloat(addr+16, (p1[0], p1[1], p1[2], 0.0), 0)
            x86.SetFloat(addr+32, (p2[0], p2[1], p2[2], 0.0), 0)

    def get(self, index):
        if index < self._size:
            addr = self._address.ptr() + index * self._item_size 
            p0 = x86.GetFloat(addr, 0, 3)
            p1 = x86.GetFloat(addr+16, 0, 3)
            p2 = x86.GetFloat(addr+32, 0, 3)
            return(p0, p1, p2)
        return None

#Buffer that stores 3 triangle points and normal of triangle 
class FlatTriangleNBuffer(Buffer):
    def __init__(self, reserve=0):
            super(FlatTriangleNBuffer, self).__init__(64, reserve)

    def add(self, p0, p1, p2, n):
        if self._reserve == self._size:
            self._resize()

        offset = self._item_size * self._size
        addr = self._address.ptr()+offset
        x86.SetFloat(addr, (p0[0], p0[1], p0[2], 0.0), 0)
        x86.SetFloat(addr+16, (p1[0], p1[1], p1[2], 0.0), 0)
        x86.SetFloat(addr+32, (p2[0], p2[1], p2[2], 0.0), 0)
        x86.SetFloat(addr+48, (n[0], n[1], n[2], 0.0), 0)
        self._size += 1

    def edit(self, index, p0, p1, p2, n):
        if index < self._size:
            addr = self._address.ptr() + index * self._item_size 
            x86.SetFloat(addr, (p0[0], p0[1], p0[2], 0.0), 0)
            x86.SetFloat(addr+16, (p1[0], p1[1], p1[2], 0.0), 0)
            x86.SetFloat(addr+32, (p2[0], p2[1], p2[2], 0.0), 0)
            x86.SetFloat(addr+48, (n[0], n[1], n[2], 0.0), 0)

    def get(self, index):
        if index < self._size:
            addr = self._address.ptr() + index * self._item_size 
            p0 = x86.GetFloat(addr, 0, 3)
            p1 = x86.GetFloat(addr+16, 0, 3)
            p2 = x86.GetFloat(addr+32, 0, 3)
            n = x86.GetFloat(addr+48, 0, 3)
            return(p0, p1, p2, n)
        return None

#Buffer that stores 3 triangle points and 3 normals one for each vertex 
class SmoothTriangleBuffer(Buffer):
    def __init__(self, reserve=0):
            super(SmoothTriangleBuffer, self).__init__(96, reserve) #TODO try with 128 perfomanse

    def add(self, p0, p1, p2, n0, n1, n2):
        if self._reserve == self._size:
            self._resize()

        offset = self._item_size * self._size
        addr = self._address.ptr()+offset
        x86.SetFloat(addr, (p0[0], p0[1], p0[2], 0.0), 0)
        x86.SetFloat(addr+16, (p1[0], p1[1], p1[2], 0.0), 0)
        x86.SetFloat(addr+32, (p2[0], p2[1], p2[2], 0.0), 0)
        x86.SetFloat(addr+48, (n0[0], n0[1], n0[2], 0.0), 0)
        x86.SetFloat(addr+64, (n1[0], n1[1], n1[2], 0.0), 0)
        x86.SetFloat(addr+80, (n2[0], n2[1], n2[2], 0.0), 0)
        self._size += 1

    def edit(self, index, p0, p1, p2, n0, n1, n2):
        if index < self._size:
            addr = self._address.ptr() + index * self._item_size 
            x86.SetFloat(addr, (p0[0], p0[1], p0[2], 0.0), 0)
            x86.SetFloat(addr+16, (p1[0], p1[1], p1[2], 0.0), 0)
            x86.SetFloat(addr+32, (p2[0], p2[1], p2[2], 0.0), 0)
            x86.SetFloat(addr+48, (n0[0], n0[1], n0[2], 0.0), 0)
            x86.SetFloat(addr+64, (n1[0], n1[1], n1[2], 0.0), 0)
            x86.SetFloat(addr+80, (n2[0], n2[1], n2[2], 0.0), 0)

    def get(self, index):
        if index < self._size:
            addr = self._address.ptr() + index * self._item_size 
            p0 = x86.GetFloat(addr, 0, 3)
            p1 = x86.GetFloat(addr+16, 0, 3)
            p2 = x86.GetFloat(addr+32, 0, 3)
            n0 = x86.GetFloat(addr+48, 0, 3)
            n1 = x86.GetFloat(addr+64, 0, 3)
            n2 = x86.GetFloat(addr+80, 0, 3)
            return(p0, p1, p2, n0, n1, n2)
        return None


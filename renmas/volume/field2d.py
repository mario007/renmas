import x86

class Field2D:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.buffer = x86.MemData(width * height * 4)
        #voxel space
        #local space - think!!

    
    def write(self, x, y, value):
        offset = y * self.width * 4 + x * 4
        adr = self.buffer.ptr() + offset 
        x86.SetFloat(adr, value, 0)

    def read(self, x, y):
        offset = y * self.width * 4 + x * 4
        adr = self.buffer.ptr() + offset 
        return x86.GetFloat(adr, 0, 0)

    def nearest_neighbor_splat(x, y, value):
        x = int(x)
        y = int(j)
        self.write(x, y, value)

    def bilinear_splat(x, y, value):
        pass

    def _cf(self, n):
        return "{:.3f}".format(n)

    def write_to_file(self, fname):
        #because of easy viewing large field
        f = open(fname, 'w')
        for j in range(self.height):
            text = ""
            for i in range(self.width):
                text += self._cf(self.read(i, j)) + ", " 
            text += "\n"
            f.write(text)
        f.close()

    def __str__(self):
        for j in range(self.height):
            text = ""
            for i in range(self.width):
                text += self._cf(self.read(i, j)) + ", " 
            text += "\n"
            print(text)
        return "" 


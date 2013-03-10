import math
from .integer import Integer
from .cgen import register_user_type

class Tile2D:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self._lst_tiles = []

    @property
    def tiles(self):
        return self._lst_tiles

    #you can recive less tiles than requested!!! Be cerful to acount for this 
    def split(self, n): #split tile to n mini-tiles
        hp = int(float(self.height) / n) + 1
        self._lst_tiles = []
        for k in range(self.y, self.y+self.height, hp):
            nh = hp
            if k > self.y + self.height - hp: 
                nh = self.y + self.height - k
            self._lst_tiles.append(Tile2D(self.x, k, self.width, nh))

    def __repr__(self):
        return ('%s x=%i y=%i w=%i h=%i ntiles=%i' % (self.__class__.__name__, self.x, self.y,
            self.width, self.height, len(self._lst_tiles)))

    @classmethod
    def user_type(cls):
        typ_name = "Tile2D"
        fields = [('x', Integer), ('y', Integer), ('width', Integer), ('height', Integer)]
        return (typ_name, fields)

register_user_type(Tile2D)

def create_tiles(width, height, spp, max_samples, nthreads):

    w = h = int(math.sqrt(max_samples / spp))
    #w = h = 50
    sx = sy = 0
    xcoords = []
    ycoords = []
    tiles = []
    while sx < width:
        xcoords.append(sx)
        sx += w
    last_w = width - (sx - w) 
    while sy < height:
        ycoords.append(sy)
        sy += h
    last_h = height - (sy - h)

    for i in xcoords:
        for j in ycoords:
            tw = w
            th = h
            if i == xcoords[-1]:
                tw = last_w
            if j == ycoords[-1]:
                th = last_h
            t = Tile2D(i, j, tw, th)
            t.split(nthreads) #multithreading
            tiles.append(t)

    return tiles


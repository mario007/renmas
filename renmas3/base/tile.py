import math

class Tile:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.lst_tiles = [] 

    #you can recive less tiles than requested!!! Be cerful to acount for this 
    def split(self, n): #split tile to n mini-tiles
        hp = int(float(self.height) / n) + 1
        self.lst_tiles = []
        for k in range(self.y, self.y+self.height, hp):
            nh = hp
            if k > self.y + self.height - hp: 
                nh = self.y + self.height - k
            self.lst_tiles.append(Tile(self.x, k, self.width, nh))

    def __repr__(self):
        return ('%s x=%i y=%i w=%i h=%i ntiles=%i' % (self.__class__.__name__, self.x, self.y, self.width, self.height,
            len(self.lst_tiles)))

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
            t = Tile(i, j, tw, th)
            t.split(nthreads) #multithreading
            tiles.append(t)

    return tiles


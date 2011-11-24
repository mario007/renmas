import math
from .structures import Structures
from .tile import Tile

_structs = Structures()

def get_structs(names):
    return _structs.structs(names)

def compiled_struct(name):
    return _structs.get_compiled_struct(name)

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


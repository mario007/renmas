
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
            if k > self.y + self.height - hp: nh = self.y + self.height - k
            self.lst_tiles.append(Tile(self.x, k, self.width, nh))

    def __repr__(self):
        return ('%s x=%i y=%i w=%i h=%i ntiles=%i' % (self.__class__.__name__, self.x, self.y, self.width, self.height,
            len(self.lst_tiles)))


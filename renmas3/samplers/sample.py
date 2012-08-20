
class Sample:
    __slots__ = ['x', 'y', 'ix', 'iy', 'weight']
    def __init__(self, x, y, ix, iy, weight):
        self.x = x 
        self.y = y 
        self.ix = ix 
        self.iy = iy 
        self.weight = weight 

    def __repr__(self):
        return 'x=%f y=%f ix=%i iy=%i weight=%f' % (self.x, self.y, self.ix, self.iy, self.weight)

    @classmethod
    def struct(cls):
        sample = """
            struct sample
            float xyxy[4] 
            uint32 ix, iy
            float weight 
            end struct
        """
        return sample 


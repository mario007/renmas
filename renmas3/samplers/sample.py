
from ..base import register_user_type, Integer, Float

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
            struct Sample
            float xyxy[4] 
            uint32 ix, iy
            float weight 
            end struct
        """
        return sample 

    @classmethod
    def user_type(cls):
        typ_name = "Sample"
        fields = [('x', Float), ('y', Float), ('ix', Integer), ('iy', Integer),
                ('weight', Float)]
        return (typ_name, fields)

register_user_type(Sample)


class Ray():
    __slots__ = ['origin', 'dir']
    def __init__(self, o, d):
        self.origin = o
        self.dir = d

    def __str__(self):
        text = "Origin = " + str(self.origin) + " \n"
        text += "Direction = " + str(self.dir)
        return text 


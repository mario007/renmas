

class Ray():

    __slots__ = ['origin', 'direction']

    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    def __str__(self):
        text = "Origin = " + str(self.origin) + " \n"
        text += "Direction = " + str(self.direction)
        return text

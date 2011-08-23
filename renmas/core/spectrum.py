
class Spectrum:
    __slots__ = ['r', 'g', 'b']
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __str__(self):
        return '(%s,%s,%s)' % (self.r, self.g, self.b)

    def __repr__(self):
        return 'Spectrum(%s,%s,%s)' % (self.r, self.g, self.b)

    def __add__(self, col):
        return Spectrum(self.r + col.r, self.g + col.g, self.b + col.b)

    def __sub__(self, col):
        return Spectrum(self.r - col.r, self.g - col.g, self.b - col.b)

    def __eq__(self, col):
        return (self.r == col.r) and (self.g == col.g) and (self.b == col.b)
    
    def __mul__(self, t):
        return Spectrum(self.r * t, self.g * t, self.b * t)

    def mix_spectrum(self, col):
        return Spectrum(self.r * col.r, self.g * col.g, self.b * col.b)

    def rgb(self):
        return (int(256*self.r), int(256*self.g), int(256*self.b))

    def scale(self, t):
        self.r = t * self.r
        self.g = t * self.g
        self.b = t * self.b
        return self

    def clamp(self):
        if self.r > 1.0: self.r = 0.99
        if self.g > 1.0: self.g = 0.99
        if self.b > 1.0: self.b = 0.99
        if self.r < 0.0: self.r = 0.0
        if self.g < 0.0: self.g = 0.0
        if self.b < 0.0: self.b = 0.0


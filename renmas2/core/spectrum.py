
class Spectrum:
    __slots__ = ['r', 'g', 'b', 'sampled', 'samples']
    def __init__(self, sampled, samples):
        self.sampled = sampled
        if sampled:
            self.samples = samples
        else:
            self.r, self.g, self.b = samples 

    def __str__(self):
        if self.sampled:
            return str(self.samples)
        else:
            return '(%s,%s,%s)' % (self.r, self.g, self.b)

    def __repr__(self):
        if self.sampled:
            return str(self.samples)
        else:
            return 'Spectrum(%s,%s,%s)' % (self.r, self.g, self.b)

    def __add__(self, col):
        if self.sampled:
            samples = [self.samples[i] + col.samples[i] for i in range(len(self.samples))]
            return Spectrum(True, samples)
        else:
            return Spectrum(False, (self.r + col.r, self.g + col.g, self.b + col.b))

    def __sub__(self, col):
        if self.sampled:
            samples = [self.samples[i] - col.samples[i] for i in range(len(self.samples))]
            return Spectrum(True, samples)
        else:
            return Spectrum(False, (self.r - col.r, self.g - col.g, self.b - col.b))

    def __eq__(self, col):
        return (self.r == col.r) and (self.g == col.g) and (self.b == col.b)
    
    def __mul__(self, t):
        if self.sampled:
            samples = [self.samples[i] * t for i in range(len(self.samples))]
            return Spectrum(True, samples)
        else:
            return Spectrum(False, (self.r * t, self.g * t, self.b * t))

    def __rmul__(self, t):
        if self.sampled:
            samples = [self.samples[i] * t for i in range(len(self.samples))]
            return Spectrum(True, samples)
        else:
            return Spectrum(False, (self.r * t, self.g * t, self.b * t))

    def mix_spectrum(self, col):
        if self.sampled:
            samples = [self.samples[i] * col.samples[i] for i in range(len(self.samples))]
            return Spectrum(True, samples)
        else:
            return Spectrum(False, (self.r * col.r, self.g * col.g, self.b * col.b))

    def rgb(self):
        return (int(256*self.r), int(256*self.g), int(256*self.b))

    def scale(self, t):
        if self.sampled:
            self.samples = [self.samples[i] * t for i in range(len(self.samples))]
        else:
            self.r = t * self.r
            self.g = t * self.g
            self.b = t * self.b
        return self

    def to_ds(self):
        if self.sampled:
            return tuple(self.samples)
        else:
            return (float(self.r), float(self.g), float(self.b), 0.0)

    def clamp(self):
        if self.r > 1.0: self.r = 0.99
        if self.g > 1.0: self.g = 0.99
        if self.b > 1.0: self.b = 0.99
        if self.r < 0.0: self.r = 0.0
        if self.g < 0.0: self.g = 0.0
        if self.b < 0.0: self.b = 0.0


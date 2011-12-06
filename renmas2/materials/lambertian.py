import math
from .brdf import BRDF

class Lambertian(BRDF):
    def __init__(self, spectrum, k=None):
        self.spectrum = spectrum * ( 1 / math.pi)
        self.k = k

    def brdf(self, hitpoint):
        if self.k:
            return self.spectrum
        else:
            return self.spectrum * self.k



from math import sqrt

class Fresnel:
    def __init__(self, F0=None, n=None, k=None):
        
        if F0 is None and n is None and k is None:
            raise ValueError("Missing fresnel arguments!!!")

        self._n = n
        self._k = k
        self._complex = False
        if F0 is not None:
            self._n = self._convert_f0(F0)
        
        if self._n is not None and self._k is not None:
            self._complex = True

    def _convert_f0(self, reflectance):
        ref = reflectance
        if ref.sampled:
            samples = [(1.0+sqrt(s))/(1.0-sqrt(s)) for s in ref.samples]
            ref.samples = samples
        else:
            ref.r = (1.0 + sqrt(ref.r)) / (1.0 - sqrt(ref.r)) 
            ref.g = (1.0 + sqrt(ref.g)) / (1.0 - sqrt(ref.g)) 
            ref.b = (1.0 + sqrt(ref.b)) / (1.0 - sqrt(ref.b)) 

    def evaluate(self, hp):
        pass


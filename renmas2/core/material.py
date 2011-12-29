
from ..materials import BRDF
from .spectrum import Spectrum

class Material:
    def __init__(self):
        self._brdfs = []
        self._btdfs = []
        self._samplers = []
        self._emiter = None

    def add(self, obj): #brdf or btdf or sampler 
        if isinstance(obj, BRDF):
            self._brdfs.append(obj)

        #TODO -- btdf sampler Log!!!

    def set_emiter(self, emiter):
        self._emiter = emiter

    def Le(self, hitpoint):
        if self._emiter:
            raise ValueError("Not yet implemented")
        else:
            return Spectrum(False, (0.0, 0.0, 0.0))

    def brdf(self, hitpoint):
        spectrum = Spectrum(False, (0.0, 0.0, 0.0)) 
        for c in self._brdfs:
            spectrum = spectrum + c.brdf(hitpoint) 
        
        #TODO -- set constraint that spectrum can be max 1.0
        hitpoint.brdf = spectrum
        return spectrum 

    def btdf(self, hitpoint):
        pass




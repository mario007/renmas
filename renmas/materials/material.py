
import renmas.core
import math

def Lambertian(R): #TODO include or dont include ndotwi - make an option
    spectrum = renmas.core.Spectrum(R, R, R) 
    def brdf(hitpoint):
        return spectrum.mix_spectrum(hitpoint.spectrum) * hitpoint.ndotwi  
    return brdf

def Phong(spectrum, e):
    def brdf(hitpoint):
        hp = hitpoint
        r = hp.normal * hp.ndotwi * 2.0 - hp.wi

        rdotwo = r.dot(hp.wo)
        if rdotwo > 0.0:
            phong = spectrum * math.pow(rdotwo, e)
            return phong.mix_spectrum(hp.spectrum) 
        return renmas.core.Spectrum(0.0, 0.0, 0.0)
    return brdf

class Material:
    def __init__(self):
        self.components = []

    def add_component(self, component):
        self.components.append(component)

    def brdf(self, hitpoint):
        spectrum = renmas.core.Spectrum(0.0, 0.0, 0.0) 
        for c in self.components:
            spectrum = spectrum + c(hitpoint)
        
        hitpoint.spectrum = spectrum


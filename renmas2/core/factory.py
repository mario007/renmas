
from tdasm import Tdasm
from ..materials import Lambertian
from ..lights import PointLight
from .spectrum import Spectrum
from .material import Material
from .vector3 import Vector3

from renmas2.macros import MacroCall, arithmetic32, arithmetic128,\
                            broadcast, macro_if, dot_product, normalization

class Factory:
    def __init__(self):
        pass

    def create_assembler(self):
        assembler = Tdasm()
        macro_call = MacroCall()
        assembler.register_macro('call', macro_call.macro_call)
        assembler.register_macro('eq128', arithmetic128)
        assembler.register_macro('eq32', arithmetic32)
        assembler.register_macro('broadcast', broadcast)
        assembler.register_macro('if', macro_if)
        assembler.register_macro('dot', dot_product)
        assembler.register_macro('normalization', normalization)
        return assembler

    def create_shape(self, **kw):
        pass

    def create_light(self, **kw):
        typ = kw.get("type")
        if typ == "point":
            p = kw.get("position")
            s = kw.get("spectrum")
            spec = Spectrum(False, (float(s[0]), float(s[1]), float(s[2])))
            pos = Vector3(float(p[0]), float(p[1]), float(p[2]))
            l = PointLight(pos, spec)
            return l


    def create_material(self, **kw): # TODO catch Exception and return None if exception ocur
        mat = Material()
        brdfs = kw.get("brdfs", None)
        if brdfs:
            for c in brdfs:
                lamb = c.get("lambertian", None)
                if lamb:
                    s = lamb.get("spectrum")
                    k = lamb.get("k", 1.0)
                    spec = Spectrum(False, (float(s[0]), float(s[1]), float(s[2])))
                    l = Lambertian(spec, float(k))
                    mat.add(l)
        return mat

    def create_sampler(self, **kw):
        pass

    def create_camera(self, **kw):
        pass

    #nspec - number of desired spectral samples
    #val - values at certain wavelength - tuple (lambda, value)
    #start - start lambda
    #end - end lambda
    def create_spectrum(self, nspec, vals, start, end):
        s = []
        for i in range(nspec):
            lambda0 = self.lerp(float(i)/float(nspec), start, end)
            lambda1 = self.lerp(float(i+1)/float(nspec), start, end)
            s.append(self._average_spectrum(vals, lambda0, lambda1))
        print(s)

    def _average_spectrum(self, vals, lambda1, lambda2):
        # out of bounds or single value
        lam1, val1 = vals[0]
        if lambda2 <= lam1: return val1 
        lam2, val2 = vals[-1]
        if lambda1 >= lam2: return val2 
        if len(vals) == 1: return val1

        # add contribution of constant segments before and after samples
        s = 0.0
        if lambda1 < lam1: 
            s += val1 * (lam1 - lambda1)
        if lambda2 > lam2:
            s += val2 * (lambda2 - lam2)
        
        # advance to first relevant wavelength segment
        i = 0
        while lambda1 > vals[i+1][0]:
            i += 1

        def interp(w, i):
            return self.lerp((w-vals[i][0])/(vals[i+1][0]-vals[i][0]), vals[i][1], vals[i+1][1])

        def average(seg_start, seg_end, i):
            return 0.5 * (interp(seg_start, i) + interp(seg_end, i)) 

        # loop over wavelength sample segments and add contributions
        n = len(vals)
        while i+1 < n and lambda2 >= vals[i][0]:
            seg_start = max(lambda1, vals[i][0])
            seg_end = min(lambda2, vals[i+1][0])
            s += average(seg_start, seg_end, i) * (seg_end - seg_start)
            i += 1
        print(lambda1, lambda2, s / (lambda2 - lambda1))
        return s / (lambda2 - lambda1)

    # linear intepolation 
    def lerp(self, t, v1, v2):
        return (1.0 - t) * v1 + t * v2


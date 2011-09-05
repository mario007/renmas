

import renmas
import math

class WardAnisotropicBRDF:
    def __init__(self, spectrum, ax, ay, k=None):
        self.spectrum = spectrum
        self.ax = ax
        self.ay = ay
        self.k = k
        self.spec2 = renmas.core.Spectrum(0.1, 0.1, 0.1)

    def brdf(self, hitpoint):

        h = hitpoint.wo + hitpoint.wi

        ax2 = 1.0/(self.ax*self.ax) 
        ay2 = 1.0/(self.ay*self.ay)
        const1 = 4.0 * math.pi * self.ax * self.ay

        vdotn = hitpoint.wo.dot(hitpoint.normal)
        if vdotn < 0.0: return renmas.core.Spectrum(0.0, 0.0, 0.0)
        ldotn = hitpoint.wi.dot(hitpoint.normal)

        const2 = math.sqrt(vdotn * ldotn)

        w = hitpoint.normal
        tv = renmas.maths.Vector3(0.0034, 1.0, 0.0071)
        v = tv.cross(w)
        v.normalize()
        u = v.cross(w)
        
        hx = h.dot(u)
        hy = h.dot(v)
        
        hdotn = h.dot(hitpoint.normal)

        exponent = (hx*hx*ax2 + hy*hy*ay2) / (hdotn*hdotn) 
        re = math.exp(-exponent)


        if self.k is None:
            s = self.spectrum * (re / (const1*const2))
            if s.r > 1.0: print(s)
            s.clamp()
            return s
        else:
            s = self.spectrum * (rez / denom) * self.k
            return s



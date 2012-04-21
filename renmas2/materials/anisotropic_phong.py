
import math
from .brdf import BRDF
from ..core import Vector3

class PhongAnisotropic(BRDF):
    def __init__(self, diffuse, specular, alpha, beta,  k=1.0, sampling=None):

        self._diffuse = diffuse
        self._specular = specular

        self._alpha = float(alpha)
        self._beta = float(beta)
        self._k = float(k)
        self._sampling = sampling

        if sampling is not None:
            if hasattr(sampling, 'alpha'):
                sampling.alpha = self._alpha
            if hasattr(sampling, 'beta'):
                sampling.beta = self._beta

    def _set_alpha(self, value):
        self._alpha = float(value)
        if self._sampling is not None:
            if hasattr(self._sampling, 'alpha'):
                self._sampling.alpha = self._alpha
    def _get_alpha(self):
        return self._alpha
    alpha = property(_get_alpha, _set_alpha)

    def _set_beta(self, value):
        self._beta = float(value)
        if self._sampling is not None:
            if hasattr(self._sampling, 'beta'):
                self._sampling.beta = self._beta
    def _get_beta(self):
        return self._beta
    beta = property(_get_beta, _set_beta)

    def _set_k(self, value):
        self._k = value
    def _get_k(self):
        return self._k
    k = property(_get_k, _set_k)

    def _set_diffuse(self, value):
        self._diffuse = value
    def _get_diffuse(self):
        return self._diffuse
    diffuse = property(_get_diffuse, _set_diffuse)

    def _set_specular(self, value):
        self._specular = value
    def _get_specular(self):
        return self._specular
    specular = property(_get_specular, _set_specular)

    def brdf(self, hp):

        h = hp.wo + hp.wi
        h.normalize()

        const1 = math.sqrt((self._alpha + 1.0) * ( self._beta + 1.0)) / (8.0 * math.pi)

        w = hp.normal
        tv = Vector3(0.0034, 1.0, 0.0071)
        v = tv.cross(w)
        v.normalize()
        u = v.cross(w)

        hdotu = h.dot(u)
        hdotv = h.dot(v)
        hdotn = h.dot(n)


    # eax pointer to hitpoint
    # in eax must return reflectance
    def brdf_asm(self, runtimes, assembler, structures):
        return ""

    def populate_ds(self, ds):
        pass

    def convert_spectrums(self, converter):
        diffuse = converter.convert_spectrum(self._diffuse)
        specular = converter.convert_spectrum(self._specular)
        self._diffuse = diffuse 
        self._specular = specular


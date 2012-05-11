
import os
import os.path
from .material import Material
from .factory import Factory
from renmas2.materials import HemisphereCos, PhongSampling
from renmas2.materials import HemisphereCos, PerfectSpecularSampling, LambertianSampling, PhongSampling
from renmas2.materials import Lambertian, Phong, OrenNayar, WardAnisotropic, PerfectSpecular, FresnelDielectric
from renmas2.materials import PerfectTransmission, PerfectTransmissionSampling

class Mtl:
    def __init__(self):
        pass

    def load(self, fname, renderer):
        if not os.path.exists(fname): return False

        f = open(fname, "r")
        self._kd = self._ks = self._ns = self._ni = self._tf = self._d = None
        self._name = None

        for line in f:
            line = line.strip()
            if line == "": continue # skip blank lines
            words = line.split()
            if words[0] == "newmtl":
                self._create_material(renderer)
                self._name = words[1]
            elif words[0] == "Kd":
                self._kd = (float(words[1]), float(words[2]), float(words[3]))
                pass
            elif words[0] == "Ks":
                self._ks = (float(words[1]), float(words[2]), float(words[3]))
                pass
            elif words[0] == "Ns":
                self._ns = (float(words[1]))
            elif words[0] == "Ni": #index of refraction
                self._ni = (float(words[1]))
            elif words[0] == "Tf":
                self._tf = (float(words[1]), float(words[2]), float(words[3]))
            elif words[0] == "d":
                try:
                    self._d = float(words[1])
                except:
                    pass

        self._create_material(renderer)
        f.close()

    def _create_material(self, ren):
        if self._kd is None and self._ks is None and self._ns is None:
            return
        factory = Factory()
        mat = Material(ren.converter.zero_spectrum())

        if self._d is not None and self._d < 0.99: #create transparent material
            print ("Uletili tu")
            if self._ni is None: self._ni = 1.0
            if self._tf is None: t_spec = ren.converter.create_spectrum((1.0, 1.0, 1.0))
            else: t_spec = ren.converter.create_spectrum(self._tf)
            r_spec = ren.converter.create_spectrum((1.0, 1.0, 1.0))
            
            # reflection component
            eta_in = r_spec.zero_spectrum().set(float(self._ni))
            eta_out = r_spec.zero_spectrum().set(1.0)
            fresnel = FresnelDielectric(eta_in, eta_out) 
            perf_spec = PerfectSpecular(r_spec, fresnel, 1.0)
            mat.add(perf_spec)
            mat.add(PerfectSpecularSampling())

            # transmission component
            eta_in2 = r_spec.zero_spectrum().set(float(self._ni))
            eta_out2 = r_spec.zero_spectrum().set(1.0)
            fresnel2 = FresnelDielectric(eta_in2, eta_out2) 

            perf_trans = PerfectTransmission(t_spec, fresnel2, 1.0)
            mat.add(perf_trans)
            sampl = PerfectTransmissionSampling(fresnel2._avg_eta_in, fresnel2._avg_eta_out)
            mat.add(sampl)
            ren.add(self._name, mat)


        elif self._ks is not None and self._kd is not None:
            diffuse = ren.converter.create_spectrum(self._kd)
            specular = ren.converter.create_spectrum(self._ks)
            lamb = factory.create_lambertian(diffuse)
            if self._ns is not None:
                spec_sampling = PhongSampling(self._ns)
                phong_specular = factory.create_phong(specular, self._ns, sampling=spec_sampling)
            else:
                spec_sampling = PhongSampling(1.0)
                phong_specular = factory.create_phong(specular, 1.0, sampling=spec_sampling)
            mat.add(lamb)
            mat.add(phong_specular)
            sampling = HemisphereCos()
            mat.add(sampling)
            mat.add(spec_sampling)
            ren.add(self._name, mat)

        elif self._kd is not None:
            diffuse = ren.converter.create_spectrum(self._kd)
            lamb = factory.create_lambertian(diffuse)
            mat.add(lamb)
            sampling = HemisphereCos()
            mat.add(sampling)
            ren.add(self._name, mat)

        self._kd = self._ks = self._ns = self._ni = self._tf = self._d = None


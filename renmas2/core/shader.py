
from ..lights import Light
from .material import Material
from .spectrum import Spectrum

class Shader:
    def __init__(self):
        # containers for materials
        self._materials = {}
        self._materials_lst = []
        self._materials_idx = {}

        # containers for lights  
        self._lights = {}
        self._lights_lst = []

    def mat_idx(self, name):
        if name in self._materials:
            return self._materials[name][1]
        return None

    def add(self, name, obj): #material or light
        if isinstance(obj, Material): #TODO check if material allready exist
            if name in self._materials:
                return #Material allread exist -- put information in log
            self._materials[name] = (obj, len(self._materials_lst)) 
            self._materials_idx[len(self._materials_lst)] = obj
            self._materials_lst.append(obj)
        elif isinstance(obj, Light):
            if name in self._lights:
                return #Light allready exist -- create log
            self._lights[name] = obj
            self._lights_lst.append(obj)

    def shade(self, hp, renderer):

        # direct illumination
        #loop through lights ALL lights strategy !!!TODO make option - one light or all light strategy
        lights = self._lights_lst
        material = self._materials_idx[hp.material]

        # emisive material
        hp.le = material.Le(hp)

        tmp_spec = Spectrum(False, (0.0, 0.0, 0.0)) 
        for light in lights:
            if light.L(hp, renderer): #light is visible
                material.brdf(hp)
                #TODO - THINK quikly put mixing of light and material in material shader
                tmp_spec = tmp_spec + (hp.spectrum.mix_spectrum(hp.brdf) * hp.ndotwi)
        hp.spectrum = tmp_spec

        # indirect illumination
        #to calculate next direction
        # first calculate next direction i pdf - next direction is in wi
        #material.next_direction(hp)
        return hp


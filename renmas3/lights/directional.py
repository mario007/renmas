
from .light import Light

class DirectionalLight(Light):
    def __init__(self, direction, spectrum, intesity_scale=1.0):
        self._direction = direction
        self._spectrum = spectrum
        self._intesity_scale = float(intesity_scale)



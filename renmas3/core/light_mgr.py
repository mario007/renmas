from ..lights import Light, EnvironmentLight

class LightManager:
    def __init__(self):

        # containers for lights  
        self._lights = {}
        self._lights_lst = []
        self._environment_light = None

    @property
    def lights(self):
        return self._lights_lst

    @property
    def environment_light(self):
        return self._environment_light

    def light_names(self):
        return self._lights.keys()

    def light(self, name):
        if name in self._lights:
            return self._lights[name]
        return None

    def convert_spectrums(self, col_mgr):
        #environment light is also in the list so everything is ok for conversion
        for l in self._lights_lst:
            l.convert_spectrums(col_mgr)

    def add(self, name, obj): #light
        if isinstance(obj, Light):
            if name in self._lights:
                return #Light allready exist -- create log
            self._lights[name] = obj
            self._lights_lst.append(obj)
        elif isinstance(obj, EnvironmentLight):
            if name in self._lights:
                return #Light allready exist -- create log
            self._lights[name] = obj
            self._lights_lst.append(obj)
            self._environment_light = obj

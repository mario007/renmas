
class LightDatabase:
    def __init__(self):
        self.lights = []

    def add_light(self, light):
        self.lights.append(light)

    def get_lights(self):
        return self.lights



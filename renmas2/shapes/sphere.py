
from ..core import Shape

class Sphere(Shape):
    def __init__(self, origin, radius, material):
        self.origin = origin
        self.radius = radius
        self.material = material


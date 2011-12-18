
import x86
from tdasm import Runtime
from .integrator import Integrator 
from ..core import Spectrum
from ..shapes import HitPoint

class Raycast(Integrator):
    def __init__(self, renderer):
        super(Raycast, self).__init__(renderer)
        self._ds = None

    def render_py(self, tile):
        sampler = self._renderer._sampler
        sampler.set_tile(tile)
        camera = self._renderer._camera
        intersector = self._renderer._intersector
        film = self._renderer._film
        shader = self._renderer._shader
        renderer = self._renderer

        background = Spectrum(0.99, 0.0, 0.0)
        hp1 = HitPoint()
        hp1.spectrum = background

        while True:
            sam = sampler.get_sample()
            if sam is None: break 
            ray = camera.ray(sam) 
            hp = intersector.isect(ray) 
            if hp:
                hp.wo = ray.dir * -1.0
                shader.shade(hp, renderer)
                film.add_sample(sam, hp)
            else:
                film.add_sample(sam, hp1) #background

    def render_asm(self, tile):
        pass

    def prepare(self):
        pass


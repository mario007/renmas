
from .structures import Structures
from .dynamic_array import DynamicArray
from ..samplers import RandomSampler
from tdasm import Runtime

class Renderer:
    def __init__(self):
        self.structures = Structures()

        #self._sampler = RandomSampler(200, 200, 1, 1.0)

    def prepare(self):
        pass

    def struct(self, name):
        return self.structures.get_compiled_struct(name)

    def _rays_in_batch(self):
        return 10000

    def _allocate_memory(self):
        self._sample_array = DynamicArray(self.struct('sample'))
        self._sample_array.add_default_instances(self._rays_in_batch())

        self._hitpoint_array = DynamicArray(self.struct('hitpoint'))
        self._hitpoint_array.add_default_instances(self._rays_in_batch())


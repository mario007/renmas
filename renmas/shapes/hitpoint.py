
class HitPoint():
     __slots__ = ['t', 'hit_point', 'normal', 'material', 'ray', 'scene']
     def __init__(self, t=0.0, hit_point=None, normal=None, material=None,
             ray=None, scene=None):
        self.t = t
        self.hit_point = hit_point
        self.normal = normal
        self.material = material
        self.ray = ray
        self.scene = None

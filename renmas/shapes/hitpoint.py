
class HitPoint():
     __slots__ = ['t', 'hit_point', 'normal', 'material', 'ray', 'scene', 'spectrum', 'visible', 'wi', 'ndotwi', 
             'wo', 'pdf', 'stop', 'brdf', 'light_pdf', 'light_normal', 'light_sample']
     def __init__(self, t=0.0, hit_point=None, normal=None, material=None,
             ray=None, scene=None):
        self.t = t
        self.hit_point = hit_point
        self.normal = normal
        self.material = material
        self.ray = ray
        self.scene = None
        self.spectrum = None
        self.visible = False
        self.wi = None
        self.ndotwi = None
        self.wo = None
        self.pdf = None
        self.stop = None
        self.brdf = None
        self.light_pdf = None
        self.light_normal = None
        self.light_sample = None


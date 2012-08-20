
class ShadePoint():
    __slots__ = ['t', 'hit', 'normal', 'material', 'ray', 'u', 'v', 'light_spectrum', 'light_position', 'wi',
             'wo', 'pdf', 'le_spectrum', 'f_spectrum', 'shape_pdf', 'shape_normal', 'shape_sample', 'specular', 'fliped']
    def __init__(self, t=0.0, hit=None, normal=None, material=None, ray=None, u=0.0, v=0.0):
        self.t = t
        self.hit = hit
        self.normal = normal
        self.material = material
        self.ray = ray
        self.u = u
        self.v = v
        self.light_spectrum = None
        self.light_position = None
        self.wi = None
        self.wo = None
        self.pdf = None
        self.le_spectrum = None
        self.f_spectrum = None
        self.shape_pdf = None
        self.shape_normal = None
        self.shape_sample = None
        self.specular = None
        self.fliped = False

    @classmethod
    def struct(cls):
        shadepoint = """
            struct shadepoint 
            float hit[4]
            float normal[4]
            float t
            uint32 material 
            float light_position[4]
            float wi[4]
            float wo[4]
            float shape_normal[4]
            float shape_sample[4]
            float pdf
            float shape_pdf
            uint32 specular
            uint32 fliped
            spectrum le_spectrum
            spectrum f_spectrum 
            spectrum light_spectrum 
            end struct
        """
        return shadepoint 


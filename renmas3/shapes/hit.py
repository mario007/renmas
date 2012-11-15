
class HitPoint():
    __slots__ = ['t', 'hit', 'normal', 'material_idx','u', 'v']
    def __init__(self, t=0.0, hit=None, normal=None, material_idx=0, u=0.0, v=0.0):
        self.t = t
        self.hit = hit
        self.normal = normal
        self.material_idx = material_idx
        self.u = u
        self.v = v

    @classmethod
    def asm_struct(cls):
        hitpoint = """
            struct Hitpoint
            float hit[4]
            float normal[4]
            float t
            float u
            float v
            int32 material_idx 
            end struct
        """
        return hitpoint



from ..base import Vec3, Integer, Float
from ..base import register_user_type

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

    @classmethod
    def populate_ds(cls, ds, hitpoint, name):
        ds[name + ".hit"] = hitpoint.hit.to_ds() 
        ds[name + ".normal"] = hitpoint.normal.to_ds() 
        ds[name + ".t"] = hitpoint.t
        ds[name + ".u"] = hitpoint.u
        ds[name + ".v"] = hitpoint.v
        ds[name + ".material_idx"] = hitpoint.material_idx

    @classmethod
    def user_type(cls):
        typ_name = "Hitpoint"
        fields = [('hit', Vec3), ('normal', Vec3), ('t', Float), ('u', Float),
                ('v', Float), ('material_idx', Integer)]
        return (typ_name, fields)

register_user_type(HitPoint)


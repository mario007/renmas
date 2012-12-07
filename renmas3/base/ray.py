
from .arg import Vec3
from .cgen import register_user_type

class Ray():
    __slots__ = ['origin', 'dir']
    def __init__(self, o, d):
        self.origin = o
        self.dir = d

    def __str__(self):
        text = "Origin = " + str(self.origin) + " \n"
        text += "Direction = " + str(self.dir)
        return text 

    @classmethod
    def asm_struct(cls):
        ray = """
            struct Ray
            float dir[4]
            float origin[4]
            end struct
        """
        return ray

    @classmethod
    def populate_ds(cls, ds, ray, name):
        ds[name + ".origin"] = ray.origin.to_ds() 
        ds[name + ".dir"] = ray.dir.to_ds()

    @classmethod
    def user_type(cls):
        typ_name = "Ray"
        fields = [('origin', Vec3), ('direction', Vec3)]
        return (typ_name, fields)

register_user_type(Ray)


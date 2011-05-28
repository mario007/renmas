
import renmas.core
import renmas.shapes

isect = renmas.shapes.isect

geometry = renmas.geometry
def lst_shapes():
    return geometry.shapes()

def visible(p1, p2):
    lst_objects = lst_shapes()
    
    direction = p2 - p1
    distance = direction.length() - 0.0001 # self intersection??? visiblity
    ray = renmas.core.Ray(p1, direction.normalize())
    hp = isect(ray, lst_objects, 999999.0)

    if hp is None or hp is False:
        return True
    else:
        if hp.t < distance:
            return False
        else:
            return True

class PointLight:
    def __init__(self, position, spectrum):
        self.position = position
        self.spectrum = spectrum

    def L(self, hitpoint):
        # 1. check visibility
        # 2. populate light vector in hitpoint and spectrum of light
        
        wi = self.position - hitpoint.hit_point
        wi.normalize()
        ndotwi = hitpoint.normal.dot(wi)
        if ndotwi < 0.0: # light strike back of object so that mean point is not visible to light. dielectric?? FIXME
            hitpoint.visible = False
            return False

        ret = visible(self.position, hitpoint.hit_point)
        if ret is False:
            hitpoint.visible = False
            return False
        else: #think copy of spectrum ?? FIXME
            hitpoint.spectrum = self.spectrum #TODO reduce intesity  1/r^2
            hitpoint.visible = True
            hitpoint.wi = wi 
            hitpoint.ndotwi = ndotwi
            return True



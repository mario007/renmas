from .light import Light

class PointLight(Light):
    def __init__(self, position, spectrum):
        self.position = position
        self.spectrum = spectrum

    def L(self, hitpoint, renderer):
        # 1. check visibility
        # 2. populate light vector in hitpoint and spectrum of light

        wi = self.position - hitpoint.hit_point
        wi.normalize()
        ndotwi = hitpoint.normal.dot(wi)
        hitpoint.wi = wi 
        hitpoint.ndotwi = ndotwi
        if ndotwi < 0.0: # ray strike back of object so that mean point is not visible to light. dielectric?? FIXME Think
            hitpoint.visible = False
            return False

        ret = renderer._intersector.visibility(self.position, hitpoint.hit_point)
        if ret:
            hitpoint.spectrum = self.spectrum #TODO reduce intesity, attenuation options  1/r^2
            hitpoint.visible = True
            return True
        else:
            hitpoint.visible = False
            return False


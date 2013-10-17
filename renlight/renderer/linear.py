
from renlight.vector import Vector3
from renlight.ray import Ray
from renlight.sdl import Shader, register_struct,\
    Vec3Arg, StructArgPtr, FloatArg, IntArg
from renlight.sdl.arr import ArrayArg

from .hitpoint import HitPoint
from .sphere import Sphere


class Intersector:
    pass


class LinearIsect(Intersector):
    def __init__(self, shp_mgr):
        self.shp_mgr = shp_mgr

    def preapre(self):
        pass

    def isect(self, ray, min_dist=99999.0):  # ray dir. must be normalized

        hit_point = False
        for shape in self.shp_mgr:
            hit = shape.isect(ray, min_dist)
            if hit is False:
                continue
            if hit.t < min_dist:
                min_dist = hit.t
                hit_point = hit
        return hit_point

    def isect_shader(self):
        origin = Vector3(0.0, 0.0, 0.0)
        direction = Vector3(0.0, 0.0, 0.0)
        ray = Ray(origin, direction)
        hitpoint = HitPoint(0.0, Vector3(0.0, 0.0, 0.0),
                            Vector3(0.0, 0.0, 0.0), 0, 0.0, 0.0)

        func_args = [StructArgPtr('ray', ray),
                     StructArgPtr('hitpoint', hitpoint),
                     FloatArg('min_dist', 99999.0)]

        args = []
        code = "hit_happend = 0\n"
        for shp_type in self.shp_mgr.shape_types():
            code1, args1 = self._get_shape_code(shp_type)
            args.extend(args1)
            code += code1
        code += "\nreturn hit_happend\n"

        shader = Shader(code=code, args=args, name='isect_scene',
                        func_args=func_args, is_func=True)
        return shader

    def _get_shape_code(self, shape_type):
        labels = {Sphere: ('num_spheres', 'sphere_array', 'isect_sphere')}

        if shape_type not in labels:
            raise ValueError("Currently unsuported shape type!", shape_type)

        num_objects, obj_array_name, isect_object = labels[shape_type]

        code = """
i = 0
while i < %s:
    shape_object = %s[i]
    ret = %s(ray, shape_object, hitpoint, min_dist)
    if ret == 1:
        hit_happend = 1
        if hitpoint.t < min_dist:
            min_dist = hitpoint.t
    i = i + 1
        """  % (num_objects, obj_array_name, isect_object)

        darr = self.shp_mgr._shape_arrays[shape_type]
        nobj = IntArg(num_objects, len(darr))
        arr_arg = ArrayArg(obj_array_name, darr)

        return code, [nobj, arr_arg]

    def visible(self, p1, p2):
        raise NotImplementedError()

    def visible_shader(self):
        pass


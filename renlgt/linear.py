
from sdl import Shader, StructArgPtr, FloatArg, IntArg, Vector3, Ray, Vec3Arg  
from sdl.arr import ArrayArg

from .hitpoint import HitPoint


class Intersector:
    pass


class LinearIsect(Intersector):
    def __init__(self, shp_mgr):
        self.shp_mgr = shp_mgr

    def prepare_accel(self):
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

    def visibility(self, p1, p2):
        epsilon = 0.00001
        direction = p2 - p1

        distance = direction.length() - epsilon # self intersection!!! visiblity
        direction.normalize()
        ray = Ray(p1, direction)

        for shape in self.shp_mgr:
            hit = shape.isect_b(ray, distance)
            if hit:
                return False 
        return True

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

        num_objects = 'num_objects_%s' % id(shape_type)
        obj_array_name = 'obj_array_%s' % id(shape_type)
        isect_object = 'ray_object_isect_%s' % id(shape_type)

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

    def visiblity_shader(self):
        func_args = [Vec3Arg('p1', Vector3(0.0, 0.0, 0.0)),
                     Vec3Arg('p2', Vector3(0.0, 0.0, 0.0))]

        code = """
epsilon = 0.00001
direction = p2 - p1
len_squared = dot(direction, direction)
distance = sqrt(len_squared) - epsilon
ray = Ray()
ray.origin = p1
ray.direction = normalize(direction)
        """
        args = []
        for shp_type in self.shp_mgr.shape_types():
            code1, args1 = self._get_visibility_code(shp_type)
            args.extend(args1)
            code += code1
        code += "\nreturn 1\n"

        shader = Shader(code=code, args=args, name='visibility',
                        func_args=func_args, is_func=True)
        return shader

    def _get_visibility_code(self, shape_type):
        num_objects = 'num_vobjects_%s' % id(shape_type)
        obj_array_name = 'obj_varray_%s' % id(shape_type)
        isect_object = 'ray_object_isect_b_%s' % id(shape_type)

        code = """
i = 0
while i < %s:
    shape_object = %s[i]
    ret = %s(ray, shape_object, distance)
    if ret == 1:
        return 0
    i = i + 1
        """  % (num_objects, obj_array_name, isect_object)

        darr = self.shp_mgr._shape_arrays[shape_type]
        nobj = IntArg(num_objects, len(darr))
        arr_arg = ArrayArg(obj_array_name, darr)
        return code, [nobj, arr_arg]

    def compile(self):
        isect_shaders = []
        for shp_type in self.shp_mgr.shape_types():
            shader_name = 'ray_object_isect_%s' % id(shp_type)
            isect = shp_type.isect_shader(shader_name)
            isect.compile()
            isect_shaders.append(isect)
        self.isect_shaders = isect_shaders

        self.shader = self.isect_shader()
        self.shader.compile([s.shader for s in isect_shaders])
        
        vis_shaders = []
        for shp_type in self.shp_mgr.shape_types():
            shader_name = 'ray_object_isect_b_%s' % id(shp_type)
            isect = shp_type.isect_b_shader(shader_name)
            isect.compile()
            vis_shaders.append(isect)
        self.vis_shaders = vis_shaders

        self.visible_shader = self.visiblity_shader()
        self.visible_shader.compile(s.shader for s in vis_shaders)

    def prepare(self, runtimes):
        for isect_shader in self.isect_shaders:
            isect_shader.prepare(runtimes)
        self.shader.prepare(runtimes)

        for vis_shader in self.vis_shaders:
            vis_shader.prepare(runtimes)
        self.visible_shader.prepare(runtimes)

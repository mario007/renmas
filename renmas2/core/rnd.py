
import os
import renmas2
import renmas2.shapes
from renmas2.core import Vector3
from renmas2.lights import PointLight
from .material import Material
from renmas2.materials import HemisphereCos
from ..cameras import Pinhole
from ..tone_mapping import PhotoreceptorOperator, ReinhardOperator


class IRender:
    def __init__(self, renderer):
        self.renderer = renderer
        self.factory = renmas2.Factory()

        #just because of speed in C# gui
        self._reinhard = ReinhardOperator()
        self._photoreceptor = PhotoreceptorOperator()
    
    def add_light(self, **kw):
        typ = kw.get("type")
        if typ == "pointlight":
            p = kw.get("position")
            s = kw.get("source")
            name = kw.get("name", None)
            scaler = kw.get("scale", None)
            #TODO -- creation of spectrum from spectrum database
            spec = self.renderer.converter.create_spectrum(s, True)
            if scaler is not None:
                spec.scale(float(scaler))
            pos = Vector3(float(p[0]), float(p[1]), float(p[2]))
            l = PointLight(pos, spec)
            self.renderer.add(name, l)
            return l

    def add_shape(self, **kw):
        t = kw.get("type", None)
        if t is None: return #log!!! TODO
        if t == "sphere": self._create_sphere(kw)
        if t == "triangle": self._create_triangle(kw)
        if t == "rectangle": self._create_rectangle(kw)
        if t == "mesh": self._create_mesh(kw)

    def add_material(self, **kw):
        t = kw.get("type", None)
        if t is None: return #log!!! TODO
        if t == "lambertian": self._create_lambertian(kw)
        if t == "phong": self._create_phong(kw)

    def _create_phong(self, kw):
        name = kw.get("name", None)
        diffuse = kw.get("diffuse", None)
        specular = kw.get("specular", None)
        n = kw.get("n", None)
        if name is None or diffuse is None or specular is None or n is None: return
        mat = Material(self.renderer.converter.zero_spectrum())
        diff = self.renderer.converter.create_spectrum(diffuse)
        spec = self.renderer.converter.create_spectrum(specular)
        n = float(n)
        lamb = self.factory.create_lambertian(diff)
        phong_specular = self.factory.create_phong(spec, n)
        mat.add(lamb)
        mat.add(phong_specular)
        sampling = HemisphereCos()
        mat.add(sampling)
        self.renderer.add(name, mat)

    def _create_lambertian(self, kw):
        name = kw.get("name", None)
        s = kw.get("source", None)
        if name is None or s is None: return
        mat = Material(self.renderer.converter.zero_spectrum())
        spec = self.renderer.converter.create_spectrum(s)
        lamb = self.factory.create_lambertian(spec)
        mat.add(lamb)
        sampling = HemisphereCos()
        mat.add(sampling)
        self.renderer.add(name, mat)

    def _create_rectangle(self, kw):
        P = kw.get("P", None)
        ea = kw.get("Edge_a", None)
        eb = kw.get("Edge_b", None)
        n = kw.get("Normal", None)
        name = kw.get("name", None)
        if name is None or P is None or ea is None or eb is None or n is None: return #LOG TODO
        rect = self.factory.create_rectangle(P, ea, eb, n)
        self.renderer.add(name, rect)
        material = kw.get("material", None)
        if material is not None:
            self.renderer.assign_material(name, material)

    def _create_triangle(self, kw):
        p0 = kw.get("P0", None)
        p1 = kw.get("P1", None)
        p2 = kw.get("P2", None)
        name = kw.get("name", None)
        if name is None or p0 is None or p1 is None or p2 is None: return #LOG TODO
        triangle = self.factory.create_triangle(v0=p0, v1=p1, v2=p2)
        self.renderer.add(name, triangle)
        material = kw.get("material", None)
        if material is not None:
            self.renderer.assign_material(name, material)

    def _create_sphere(self, kw):
        radius = kw.get("radius", None)
        position = kw.get("position", None)
        name = kw.get("name", None)
        if radius is None or position is None or name is None: return #LOG TODO
        sph = self.factory.create_sphere(origin=position, radius=radius)
        self.renderer.add(name, sph)
        material = kw.get("material", None)
        if material is not None:
            self.renderer.assign_material(name, material)

    def _create_from_ply(self, kw):
        name = kw.get("name", None)
        filename = kw.get("filename", None)
        material = kw.get("material", None)
        ply = renmas2.core.Ply()
        ply.load(filename)
        vb = ply.vertex_buffer
        tb = ply.triangle_buffer
        mesh = self.factory.create_mesh(vb, tb)
        self.renderer.add(name, mesh)
        if material is not None:
            self.renderer.assign_material(name, material)

    def _create_from_obj(self, kw):
        name = kw.get("name", None)
        filename = kw.get("filename", None)
        material = kw.get("material", None)
        mtl_fname = kw.get("mtl", None)
        if mtl_fname is not None:
            mtl = renmas2.core.Mtl()
            mtl.load(mtl_fname, self.renderer)

        obj = renmas2.core.Obj()
        ret = obj.load(filename)
        if ret is False: return # file is not corretly loaded! TODO log
        meshes = obj.meshes
        for m in meshes:
            mesh = self.factory.create_mesh(m.vb, m.tb)
            self.renderer.add(m.name, mesh)
            self.renderer.assign_material(m.name, m.mat_name)

    def _create_mesh(self, kw):
        name = kw.get("name", None)
        filename = kw.get("filename", None)
        material = kw.get("material", None)

        if name is None or filename is None: return #LOG TODO
        fname, ext = os.path.splitext(filename)
        if ext == ".ply":
            self._create_from_ply(kw)
        elif ext == ".obj":
            self._create_from_obj(kw)


    def options(self, **kw):
        asm = kw.get("asm", None)
        if asm is not None: self.renderer.asm = bool(asm)
        spectral = kw.get("spectral", None)
        if spectral is not None: self.renderer.spectral_rendering = bool(spectral)
        pixel_size = kw.get("pixel_size", None)
        if pixel_size is not None: self.renderer.pixel_size = pixel_size
        width = self.renderer._width 
        height = self.renderer._height
        w = kw.get("width", width)
        h = kw.get("height", height)
        self.renderer.resolution(w, h)
        spp = self.renderer.spp
        s = kw.get("spp", spp)
        self.renderer.spp = s 
        threads = self.renderer.threads
        n = kw.get("threads", spp)
        self.renderer.threads = n

    def create_samplers(self, **kw):
        pass

    def set_camera(self, **kw):
        t = kw.get("type", None)
        if t is None: return #log!!! TODO
        #TODO -- implementation of other types of cameras
        eye = kw.get("eye", None)
        lookat = kw.get("lookat", None)
        distance = kw.get("distance", None)
        if eye is not None and lookat is not None and distance is not None:
            camera = Pinhole(eye=eye, lookat=lookat, distance=distance)
            self.renderer.set_camera(camera)

    def set_props(self, category, name, value):
        if category == "camera":
            self._set_camera_props(name, value)
        elif category == "misc":
            self._set_misc(name, value)
        elif category == "light_position":
            self._set_light_position(name, value)
        elif category == "light_spectrum_scale":
            self._scale_light_spectrum(name, value)
        elif category == "light_intesity":
            self._set_light_intesity(name, value)
        elif category == "material_assign":
            self.renderer.assign_material(name, value)
        elif category == "ReinhardOperator":
            self._set_reinhard_props(name, value)
        elif category == "PhotoreceptorOperator":
            self._set_photoreceptor_props(name, value)
        return 1

    def get_props(self, category, name):
        if category == "camera":
            return self._get_camera_props(name)
        elif category == 'misc':
            return self._get_misc(name)
        elif category == "frame_buffer":
            fb = self.renderer.film.frame_buffer
            w, h = fb.get_size()
            ptr, pitch = fb.get_addr()
            return str(w) + "," + str(h) + "," + str(pitch) + "," + str(ptr) 
        elif category == "light":
            return self._get_light_props(name)
        elif category == "light_type":
            return self._get_light_type(name)
        elif category == "light_position":
            return self._get_light_position(name)
        elif category == "light_intesity":
            return self._get_light_intesity(name)
        elif category == "material_name":
            return self._get_material_name(name)
        elif category == "ReinhardOperator":
            return self._get_reinhard_props(name)
        elif category == 'PhotoreceptorOperator':
            return self._get_photoreceptor_props(name)
        return ""

    def _get_photoreceptor_props(self, name):
        tm = self.renderer.tone_mapping_operator
        if isinstance(tm, PhotoreceptorOperator):
            if name == "contrast":
                return str(tm.m) 
            elif name == "adaptation":
                return str(tm.c)
            elif name == "colornes":
                return str(tm.a)
            elif name == "lightnes":
                return str(tm.f)
            else:
                return '0.0'
        return '0.0'

    def _set_photoreceptor_props(self, name, value):
        tm = self.renderer.tone_mapping_operator
        if isinstance(tm, PhotoreceptorOperator):
            if name == "contrast":
                tm.m = value
            elif name == "adaptation":
                tm.c = value
            elif name == "colornes":
                tm.a = value
            elif name == "lightnes":
                tm.f = value

    def _get_reinhard_props(self, name):
        tm = self.renderer.tone_mapping_operator
        if isinstance(tm, ReinhardOperator):
            if name == "scene_key":
                return str(tm.scene_key)
            elif name == "saturation":
                return str(tm.saturation)
            else:
                return "0.0"
        return "0.0" 

    def _set_reinhard_props(self, name, value):
        tm = self.renderer.tone_mapping_operator
        if isinstance(tm, ReinhardOperator):
            if name == "scene_key":
                tm.scene_key = value
            elif name == "saturation":
                tm.saturation = value

    def _get_material_name(self, shape_name):
        shape = self.renderer.intersector.shape(shape_name)
        if shape is None: return ""
        mat_name = self.renderer.shader.material_name(shape.material)
        if mat_name:
            return mat_name
        return "" 

    def _scale_light_spectrum(self, name, value):
        light = self.renderer.shader.light(name)
        if light is None: return
        light.spectrum = light.spectrum * float(value)

    def _set_light_intesity(self, name, value):
        val = value.split(',')
        if len(val) != 2: return
        w, v = val
        light = self.renderer.shader.light(name)
        if light is None: return ""
        s = light.spectrum
        if s.sampled:
            lambdas = self.renderer.converter.lambdas() 
            for i in range(len(s.samples)):
                if str(int(lambdas[i])) == w: s.samples[i] = float(v) 
            light.spectrum = s

        else:
            if w == "RED": s.r = float(v) 
            if w == "GREEN": s.g = float(v)
            if w == "BLUE": s.b = float(v)
            light.spectrum = s

    def _get_light_intesity(self, name):
        light = self.renderer.shader.light(name)
        if light is None: return ""
        s = light.spectrum
        if s.sampled:
            ret = ""
            sam = s.samples
            for i in range(len(sam)):
                ret += str(sam[i]) + ','
            if ret != "":
                return ret[:-1]
        else:
            return str(s.r) + "," + str(s.g) + "," + str(s.b) 
        return ""
        

    def _get_light_type(self, name):
        light = self.renderer.shader.light(name)
        if light is None: return ""
        elif type(light) == PointLight: return "PointLight"
        return ""

    def _set_light_position(self, name, value):
        light = self.renderer.shader.light(name)
        if light is None: return ""
        elif type(light) == PointLight:
            words = value.split(',')
            if len(words) == 3:
                x, y, z = words
                pos = Vector3(float(x), float(y), float(z))
                light.position = pos

    def _get_light_position(self, name):
        light = self.renderer.shader.light(name)
        if light is None: return ""
        elif type(light) == PointLight: 
            p = light.position
            return str(p.x) + "," + str(p.y) + "," + str(p.z)
        return ""

    def _get_light_props(self, name):
        if name == "light_names":
            return ",".join(self.renderer.shader.light_names())

    def _set_camera_props(self, name, value):
        if name == "eye":
            x, y, z = value.split(',')
            self.renderer.camera.set_eye(x, y, z)
        elif name == "lookat":
            x, y, z = value.split(',')
            self.renderer.camera.set_lookat(x, y, z)
        elif name == "distance":
            self.renderer.camera.set_distance(value)

    def _get_camera_props(self, name):
        if name == "eye":
            x, y, z = self.renderer.camera.get_eye()
            return str(x) + "," + str(y) + "," + str(z) 
        elif name == "lookat":
            x, y, z = self.renderer.camera.get_lookat()
            return str(x) + "," + str(y) + "," + str(z) 
        elif name == "distance":
            return str(self.renderer.camera.get_distance())
        return ""

    def _set_misc(self, name, value):
        if name == "resolution":
            w, h = value.split(',')
            self.renderer.resolution(w, h)
        elif name == "spp":
            self.renderer.spp = value
        elif name == "pixel_size":
            self.renderer.pixel_size = value
        elif name == "threads":
            self.renderer.threads = value
        elif name == "asm":
            if value == "False" or value == 'false': 
                self.renderer.asm = False
            else:
                self.renderer.asm = True 
        elif name == "spectral":
            if value == "False" or value == 'false':
                self.renderer.spectral_rendering = False
            else:
                self.renderer.spectral_rendering = True
        elif name == "tone_mapping":
            if value == "False" or value == 'false': 
                self.renderer.tone_mapping = False
            else:
                self.renderer.tone_mapping = True 
        elif name == "selected_operator":
            if value == "Reinhard":
                self.renderer.tone_mapping_operator = self._reinhard 
            elif value == "Photoreceptor":
                self.renderer.tone_mapping_operator = self._photoreceptor 

    def _get_misc(self, name):
        if name == 'resolution':
            return str(self.renderer._width) + ',' + str(self.renderer._height)
        elif name == 'spp':
            return str(self.renderer.spp)
        elif name == 'pixel_size':
            return str(self.renderer.pixel_size)
        elif name == 'threads':
            return str(self.renderer.threads)
        elif name == 'asm':
            return str(self.renderer.asm)
        elif name == 'spectral':
            return str(self.renderer.spectral_rendering)
        elif name == 'lambdas':
            lambdas = self.renderer.converter.lambdas() 
            return ",".join([str(int(l)) for l in lambdas])
        elif name == "log":
            return self.renderer.get_log()
        elif name == "shapes":
            names = self.renderer.intersector.names()
            if names is None: return ""
            return ",".join(names)
        elif name == "materials":
            names = self.renderer.shader.material_names()
            if names is None: return ""
            return ",".join(names)
        elif name == 'tone_mapping_operators':
            return "Reinhard,Photoreceptor"
        elif name == 'tone_mapping':
            return str(self.renderer.tone_mapping)
        elif name == "selected_operator":
            tm = self.renderer.tone_mapping_operator
            if isinstance(tm, ReinhardOperator):
                return "Reinhard"
            elif isinstance(tm, PhotoreceptorOperator):
                return "Photoreceptor"
            else:
                return ""
        else:
            return ""



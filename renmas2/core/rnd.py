
import os
import renmas2
import renmas2.shapes
from renmas2.core import Vector3
from renmas2.lights import PointLight, ConstEnvironmentLight, SunSky
from .material import Material
from renmas2.materials import HemisphereCos, PerfectSpecularSampling, LambertianSampling, PhongSampling
from ..cameras import Pinhole
from ..tone_mapping import PhotoreceptorOperator, ReinhardOperator
from ..materials import Lambertian, Phong, OrenNayar, WardAnisotropic, PerfectSpecular, FresnelDielectric
from ..materials import PerfectTransmission, PerfectTransmissionSampling

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
            if type(s) == str:
                s = self.renderer.spd.load("light", s)
                if s is None: return None

            spec = self.renderer.converter.create_spectrum(s, True)
            if scaler is not None:
                spec.scale(float(scaler))
            pos = Vector3(float(p[0]), float(p[1]), float(p[2]))
            l = PointLight(pos, spec)
            self.renderer.add(name, l)
            return l
        elif typ == "environment":
            s = kw.get("source")
            name = kw.get("name", None)
            spec = self.renderer.converter.create_spectrum(s, True)
            l = ConstEnvironmentLight(spec)
            self.renderer.add(name, l)
            return l
        elif typ == "sunsky":
            name = kw.get("name", None)
            lat = kw.get("latitude")
            lon = kw.get("longitude")
            sm = kw.get("sm")
            jd = kw.get("jd")
            tm = kw.get("time_of_day")
            turbidity = kw.get("turbidity")
            sk = SunSky(self.renderer, lat, lon, sm, jd, tm, turbidity)
            self.renderer.add(name, sk)

    def add_shape(self, **kw):
        t = kw.get("type", None)
        if t is None: return #log!!! TODO
        if t == "sphere": self._create_sphere(kw)
        if t == "triangle": self._create_triangle(kw)
        if t == "rectangle": self._create_rectangle(kw)
        if t == "mesh": self._create_mesh(kw)

    def add_material(self, **kw):
        components = kw.get("components", None)
        if components is not None:
            self._create_material(kw)
        t = kw.get("type", None)
        if t is None: return #log!!! TODO
        if t == "lambertian": self._create_lambertian(kw)
        if t == "phong": self._create_phong(kw)

    def _add_brdf_samplings(self, mat, samplings):
        if samplings is None:
            #mat.add(HemisphereCos())
            mat.add(LambertianSampling())
            return
        samplings = samplings.split(',')
        for s in samplings:
            s = s.strip()
            if s == "perfect_specular":
                mat.add(PerfectSpecularSampling())
            elif s == "lambertian" or s == "default":
                #mat.add(HemisphereCos())
                mat.add(LambertianSampling())

    def _create_phong(self, kw):
        name = kw.get("name", None)
        diffuse = kw.get("diffuse", None)
        specular = kw.get("specular", None)
        sampling = kw.get("samplings", None)
        n = kw.get("n", None)
        if name is None or diffuse is None or specular is None or n is None: return
        mat = Material(self.renderer.converter.zero_spectrum())

        if type(diffuse) == str:
            diffuse = self.renderer.spd.load("real_object", diffuse)
            if diffuse is None: return None
        diff = self.renderer.converter.create_spectrum(diffuse)

        if type(specular) == str:
            specular = self.renderer.spd.load("real_object", specular)
            if specular is None: return None
        spec = self.renderer.converter.create_spectrum(specular)

        n = float(n)
        ph = PhongSampling(n)
        mat.add(ph)
        lamb = self.factory.create_lambertian(diff)
        phong_specular = self.factory.create_phong(spec, n, sampling=ph)
        mat.add(lamb)
        mat.add(phong_specular)
        self._add_brdf_samplings(mat, sampling)
        self.renderer.add(name, mat)

    def _create_lambertian(self, kw):
        name = kw.get("name", None)
        s = kw.get("source", None)
        sampling = kw.get("samplings", None)
        if name is None or s is None: return
        mat = Material(self.renderer.converter.zero_spectrum())
        if type(s) == str:
            s = self.renderer.spd.load("real_object", s)
            if s is None: return None
        spec = self.renderer.converter.create_spectrum(s)
        lamb = self.factory.create_lambertian(spec)
        mat.add(lamb)
        self._add_brdf_samplings(mat, sampling)
        self.renderer.add(name, mat)

    def _add_lambertian_component(self, mat, comp):
        diffuse = comp.get("diffuse", None)
        if type(diffuse) == str:
            diffuse = self.renderer.spd.load("real_object", diffuse)
        spectrum = self.renderer.converter.create_spectrum(diffuse)
        lamb = self.factory.create_lambertian(spectrum)
        mat.add(lamb)

    def _add_phong_component(self, mat, comp):
        specular = comp.get("specular", None)
        if type(specular) == str:
            specular = self.renderer.spd.load("real_object", specular)
        spectrum = self.renderer.converter.create_spectrum(specular)
        n = comp.get("n", 1.0)
        sampling = comp.get("sampling", None)
        if sampling is not None:
            if sampling == "phong":
                ph = PhongSampling(n)
                mat.add(ph)
                phong_specular = self.factory.create_phong(spectrum, n, k=1.0, sampling=ph)
            else:
                phong_specular = self.factory.create_phong(spectrum, n, k=1.0)
        else:
            phong_specular = self.factory.create_phong(spectrum, n, k=1.0)
        mat.add(phong_specular)

    def _add_ward_component(self, mat, comp):
        specular = comp.get("specular", None)
        if type(specular) == str:
            specular = self.renderer.spd.load("real_object", specular)
        spectrum = self.renderer.converter.create_spectrum(specular)
        alpha = comp.get("alpha", None)
        beta = comp.get("beta", None)
        if alpha is None or beta is None:
            #TODO log
            return
        ward_specular = self.factory.create_ward(spectrum, alpha, beta, k=1.0, sampling=None)
        mat.add(ward_specular)

    def _add_oren_component(self, mat, comp):
        diffuse = comp.get("diffuse", None)
        if type(diffuse) == str:
            diffuse = self.renderer.spd.load("real_object", diffuse)
        spectrum = self.renderer.converter.create_spectrum(diffuse)
        roughness = comp.get("roughness", 0.40)
        oren = self.factory.create_oren_nayar(spectrum, 0.45) 
        mat.add(oren)

    def _add_perfect_specular_component(self, mat, comp):
        specular = comp.get("specular", None)
        if type(specular) == str:
            specular = self.renderer.spd.load("real_object", specular)
        spectrum = self.renderer.converter.create_spectrum(specular)
        ior = comp.get("ior", None)
        if ior is None: raise ValueError("Missing ior")
        eta_in = spectrum.zero_spectrum().set(float(ior))
        eta_out = spectrum.zero_spectrum().set(1.0)
        fresnel = FresnelDielectric(eta_in, eta_out) 

        perf_spec = PerfectSpecular(spectrum, fresnel, 1.0)
        mat.add(perf_spec)
        mat.add(PerfectSpecularSampling())

    def _add_perfect_transmission_component(self, mat, comp):
        specular = comp.get("specular", None)
        if type(specular) == str:
            specular = self.renderer.spd.load("real_object", specular)
        spectrum = self.renderer.converter.create_spectrum(specular)
        ior = comp.get("ior", None)
        if ior is None: raise ValueError("Missing ior")
        eta_in = spectrum.zero_spectrum().set(float(ior))
        eta_out = spectrum.zero_spectrum().set(1.0)
        fresnel = FresnelDielectric(eta_in, eta_out) 

        sampl = PerfectTransmissionSampling(fresnel._avg_eta_in, fresnel._avg_eta_out)
        perf_trans = PerfectTransmission(spectrum, fresnel, 1.0, sampl)
        mat.add(perf_trans)
        mat.add(sampl)

    # TODO -- urgent make consistent material creation -- samplings!!!!
    # predifined functions and commponent
    # TIP -- type: general -- add material components
    # type: predifined types -- they have function that add that type of material
    def _create_material(self, kw):
        name = kw.get("name", None)
        samplings = kw.get("samplings", None)
        if name is None: return
        mat = Material(self.renderer.converter.zero_spectrum())
        if samplings is None:
            pass
            #mat.add(HemisphereCos())
        else:
            self._add_brdf_samplings(mat, samplings)
        components = kw.get("components")
        for comp in components:
            typ = comp.get("type")
            if typ == "lambertian":
                self._add_lambertian_component(mat, comp)
            elif typ == "phong":
                self._add_phong_component(mat, comp)
            elif typ == "oren":
                self._add_oren_component(mat, comp)
            elif typ == "ward":
                self._add_ward_component(mat, comp)
            elif typ == "perfect_specular":
                self._add_perfect_specular_component(mat, comp)
            elif typ == "perfect_transmission":
                self._add_perfect_transmission_component(mat, comp)
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
        elif category == "light_spectrum_scale":
            self._scale_light_spectrum(name, value)
        elif category == "material_assign":
            self.renderer.assign_material(name, value)
        elif category == "ReinhardOperator":
            self._set_reinhard_props(name, value)
        elif category == "PhotoreceptorOperator":
            self._set_photoreceptor_props(name, value)
        elif category == "material_params":
            self._set_material_param(name, value)
        elif category == "light_params":
            self._set_light_param(name, value)
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
        elif category == "material_name":
            return self._get_material_name(name)
        elif category == "ReinhardOperator":
            return self._get_reinhard_props(name)
        elif category == 'PhotoreceptorOperator':
            return self._get_photoreceptor_props(name)
        elif category == 'material_components':
            return self._get_material_components(name)
        elif category == "component_type":
            return self._get_component_type(name)
        elif category == "material_params":
            return self._get_material_param(name)
        elif category == "light_params":
            return self._get_light_param(name)
        return ""

    def _get_light_param(self, value):
        val = value.split(',')
        if len(val) != 2: return ""
        light_name, param_name = val
        light = self.renderer.shader.light(light_name)
        if light is None: return ""
        if param_name == "position":
            if hasattr(light, 'position'):
                p = light.position
                return str(p.x) + "," + str(p.y) + "," + str(p.z)
            return ""
        elif param_name == "intesity":
            return self._spectrum_to_string(light.spectrum)
        elif param_name == "intesity_scale":
            if hasattr(light, 'intesity_scale'):
                return str(light.intesity_scale)
            return ""
        else:
            return ""

    def _set_light_param(self, value, param_value):
        val = value.split(',')
        if len(val) != 2: return
        light_name, param_name = val
        light = self.renderer.shader.light(light_name)
        if light is None: return 
        if param_name == "position":
            if hasattr(light, 'position'):
                words = param_value.split(',')
                if len(words) == 3:
                    x, y, z = words
                    light.position = Vector3(float(x), float(y), float(z))
        elif param_name == "intesity":
            words = param_value.split(',')
            if len(words) == 2:
                w, v = words 
                s = self._set_spectrum_value(light.spectrum, w, v)
                light.spectrum = s
        elif param_name == "intesity_scale":
            if hasattr(light, 'intesity_scale'):
                light.intesity_scale = float(param_value)

    def _get_component_type(self, name):
        val = name.split(',')
        if len(val) != 2: return ""
        mat_name, comp_name = val
        material = self.renderer.shader.material(mat_name)
        if material is None: return ""
        if comp_name.startswith('brdf'):
            components = material._brdfs
        elif comp_name.startswith('btdf'):
            return "PerfectTransmission"
        else:
            return ""
        try:
            num = int(comp_name[4:])
            comp = components[num]
            return self._get_component_name(comp)
        except:
            return ""

    def _get_component_name(self, component):
        if type(component) == Lambertian:
            return "Lambertian"
        elif type(component) == Phong:
            return "PhongSpecular"
        elif type(component) == OrenNayar:
            return "OrenNayar"
        elif type(component) == WardAnisotropic:
            return "WardAnisotropic"
        elif type(component) == PerfectSpecular:
            return "PerfectSpecular"
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

    def _get_material_components(self, name):
        material = self.renderer.shader.material(name)
        if material is None:
            return ""
        all_names = ["brdf"+ str(c) for c in range(len(material._brdfs))]
        if material._btdf is not None:
            all_names.append("btdf") 
        return ",".join(all_names)

    def _get_material_name(self, shape_name):
        shape = self.renderer.intersector.shape(shape_name)
        if shape is None: return ""
        mat_name = self.renderer.shader.material_name(shape.material)
        if mat_name:
            return mat_name
        return "" 

    def _get_material_component(self, mat_name, comp_name):
        material = self.renderer.shader.material(mat_name)
        if material is None: return None 
        if comp_name.startswith('brdf'):
            components = material._brdfs
        elif comp_name.startswith('btdf'):
            return material._btdf
        else:
            return None 
        try:
            num = int(comp_name[4:])
            return components[num]
        except:
            return None 

    def _spectrum_to_string(self, spec):
        if spec.sampled:
            return ",".join([str(l) for l in spec.samples])
        else:
            return str(spec.r) + "," + str(spec.g) + "," + str(spec.b) 
    
    def _rgb_reflectance(self, spectrum):
        r, g, b = self.renderer.converter.to_rgb(spectrum) 
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)
        if r < 0: r = 0
        if g < 0: g = 0
        if b < 0: b = 0
        if r > 255: r = 255
        if g > 255: g = 255
        if b > 255: b = 255

        return "%s,%s,%s" % (r, g, b) 
    
    def _create_spectrum(self, rgb):
        val = rgb.split(',')
        if len(val) != 3:
            return self.renderer.converter.zero_spectrum()
        r = float(val[0]) / 255.0
        g = float(val[1]) / 255.0
        b = float(val[2]) / 255.0
        return self.renderer.converter.create_spectrum([r, g, b])

    def _get_param_value(self, component, param_name):
        if type(component) == Lambertian:
            if param_name == "reflectance":
                return self._spectrum_to_string(component.spectrum)
            elif param_name == "rgb_reflectance":
                return self._rgb_reflectance(component.spectrum)
            elif param_name == "scaler":
                return str(component.k)
        elif type(component) == Phong:
            if param_name == "reflectance":
                return self._spectrum_to_string(component.spectrum)
            elif param_name == "rgb_reflectance":
                return self._rgb_reflectance(component.spectrum)
            elif param_name == "shinines":
                return str(component.n)
            elif param_name == "scaler":
                return str(component.k)
        elif type(component) == OrenNayar:
            if param_name == "reflectance":
                return self._spectrum_to_string(component.spectrum)
            elif param_name == "rgb_reflectance":
                return self._rgb_reflectance(component.spectrum)
            elif param_name == "roughness":
                return str(component.roughness)
            elif param_name == "scaler":
                return str(component.k)
        elif type(component) == WardAnisotropic:
            if param_name == "reflectance":
                return self._spectrum_to_string(component.spectrum)
            elif param_name == "rgb_reflectance":
                return self._rgb_reflectance(component.spectrum)
            elif param_name == "alpha":
                return str(component.alpha)
            elif param_name == "beta":
                return str(component.beta)
            elif param_name == "scaler":
                return str(component.k)
        elif type(component) == PerfectSpecular or type(component) == PerfectTransmission:
            if param_name == "reflectance":
                return self._spectrum_to_string(component.spectrum)
            elif param_name == "rgb_reflectance":
                return self._rgb_reflectance(component.spectrum)
            elif param_name == "simple_ior":
                return str(component.simple_ior)
            elif param_name == "scaler":
                return str(component.k)
        return ""

    def _set_param_value(self, component, param_name, value):
        if type(component) == Lambertian:
            if param_name == "reflectance":
                lam, val = value.split(',')
                s = self._set_spectrum_value(component.spectrum, lam, val)
                component.spectrum = s
            elif param_name == "rgb_reflectance":
                s = self._create_spectrum(value)
                component.spectrum = s
            elif param_name == "scaler":
                component.k = float(value)
        elif type(component) == Phong:
            if param_name == "reflectance":
                lam, val = value.split(',')
                s = self._set_spectrum_value(component.spectrum, lam, val)
            elif param_name == "rgb_reflectance":
                s = self._create_spectrum(value)
                component.spectrum = s
            elif param_name == "shinines":
                component.n = float(value)
            elif param_name == "scaler":
                component.k = float(value)
        elif type(component) == OrenNayar:
            if param_name == "reflectance":
                lam, val = value.split(',')
                s = self._set_spectrum_value(component.spectrum, lam, val)
            elif param_name == "rgb_reflectance":
                s = self._create_spectrum(value)
                component.spectrum = s
            elif param_name == "roughness":
                component.roughness = float(value)
            elif param_name == "scaler":
                component.k = float(value)
        elif type(component) == WardAnisotropic:
            if param_name == "reflectance":
                lam, val = value.split(',')
                s = self._set_spectrum_value(component.spectrum, lam, val)
            elif param_name == "rgb_reflectance":
                s = self._create_spectrum(value)
                component.spectrum = s
            elif param_name == "alpha":
                component.alpha = float(value)
            elif param_name == "beta":
                component.beta = float(value)
            elif param_name == "scaler":
                component.k = float(value)
        elif type(component) == PerfectSpecular or type(component) == PerfectTransmission:
            if param_name == "reflectance":
                lam, val = value.split(',')
                s = self._set_spectrum_value(component.spectrum, lam, val)
            elif param_name == "rgb_reflectance":
                s = self._create_spectrum(value)
                component.spectrum = s
            elif param_name == "simple_ior":
                component.ior = float(value)
            elif param_name == "scaler":
                component.k = float(value)


    def _get_material_param(self, name):
        val = name.split(',')
        if len(val) != 3: return ""
        mat_name, comp_name, param_name = val
        component = self._get_material_component(mat_name, comp_name)
        if component is None: return ""
        return self._get_param_value(component, param_name)

    def _set_material_param(self, name, value):
        val = name.split(',')
        if len(val) != 3: return
        mat_name, comp_name, param_name = val
        component = self._get_material_component(mat_name, comp_name)
        if component is None: return
        self._set_param_value(component, param_name, value)

    def _scale_light_spectrum(self, name, value):
        light = self.renderer.shader.light(name)
        if light is None: return
        light.spectrum = light.spectrum * float(value)

    def _set_spectrum_value(self, spectrum, lam, value):
        if spectrum.sampled:
            lambdas = self.renderer.converter.lambdas() 
            for i in range(len(spectrum.samples)):
                if str(int(lambdas[i])) == lam: spectrum.samples[i] = float(value) 
        else:
            if lam == "RED": spectrum.r = float(value) 
            elif lam == "GREEN": spectrum.g = float(value)
            elif lam == "BLUE": spectrum.b = float(value)
        return spectrum

    def _get_light_type(self, name):
        light = self.renderer.shader.light(name)
        if light is None: return ""
        elif type(light) == PointLight: return "PointLight"
        elif type(light) == ConstEnvironmentLight: return "ConstEnvironmentLight"
        return ""

    def _get_light_props(self, name):
        if name == "light_names":
            return ",".join(self.renderer.shader.light_names())
        return ""

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
        elif name == "project_save":
            self.renderer.save_project(value)
        elif name == "project_load":
            self.renderer.load_project(value)

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



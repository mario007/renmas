
import renmas
from ..maths import Vector3
from . import Spectrum 

#High level utility interface for Renderer
class RendererUtils:
    def __init__(self, renderer=None):
        self.renderer = renderer 
        #logger??

    def set_renderer(self, renderer):
        self.renderer = renderer 

    def create_light(self, props): #AREA LIGHT???

        typ_light = props.get("type", "")
        if typ_light == "point":
            return self._create_point_light(props)
        elif typ_light == "area":
            return create_area_light(props)
        else:
            #logger
            raise ValueError("unknown type of light")
    
    def _create_point_light(self, props):
        name = props.get("name", "light" + str(renmas.utils.unique()))
        x, y, z = props["position"]
        r, g, b, = props["spectrum"]

        spectrum = renmas.core.Spectrum(float(r), float(g), float(b))
        pos = renmas.maths.Vector3(float(x), float(y), float(z))
        plight = renmas.lights.PointLight(pos, spectrum) 

        if self.renderer is not None: self.renderer.add_light(name, plight)

        return plight

    def create_shape(self, props):
        type_shape = props.get("type", "")
        if type_shape == "sphere":
            return self._create_sphere(props) 
        elif type_shape == "triangle":
            return self._create_triangle(props)
        elif type_shape == "rectangle":
            return self._create_rectangle(props)
        elif type_shape == "mesh":
            return self._create_mesh(props)
        else:
            raise ValueError("unknown type of shape") #logger

    def _create_sphere(self, props):
        x, y, z = props["position"]
        radius = props["radius"]
        #if material is not specified we put default material
        mat_name = props.get("material", None)
        name = props.get("name", "Sphere" + str(renmas.utils.unique()))

        if mat_name is None: #logger
            print("Material doesnt exist, default material is put on shape")
            mat_name = "default_material"

        idx = self.renderer.material_index(mat_name)

        v1 = renmas.maths.Vector3(float(x), float(y), float(z))
        sphere = renmas.shapes.Sphere(v1, float(radius), idx)
        self.renderer.add_shape(name, sphere)

        return sphere

    def _create_triangle(self, props):
        x0, y0, z0 = props["p0"] 
        x1, y1, z1 = props["p1"] 
        x2, y2, z2 = props["p2"] 
        mat_name = props.get("material", None)
        if mat_name is None: #logger
            mat_name = "default_material"

        mat_idx = self.renderer.material_index(mat_name)
        name = props.get("name", "Triangle" + str(renmas.utils.unique()))

        p0 = renmas.maths.Vector3(float(x0), float(y0), float(z0))
        p1 = renmas.maths.Vector3(float(x1), float(y1), float(z1))
        p2 = renmas.maths.Vector3(float(x2), float(y2), float(z2))
        tri = renmas.shapes.Triangle(p0, p1, p2, mat_idx)

        self.renderer.add_shape(name, tri)
        return tri

    def _create_rectangle(self, props):
        x, y, z = props["p"] 
        nx, ny, nz = props["normal"] 
        eda_x, eda_y, eda_z = props["edge_a"] 
        edb_x, edb_y, edb_z = props["edge_b"] 
        mat_name = props.get("material", None)
        if mat_name is None: #logger
            mat_name = "default_material"
        mat_idx = self.renderer.material_index(mat_name)
        name = props.get("name", "Rectangle" + str(renmas.utils.unique()))

        p = renmas.maths.Vector3(float(x), float(y), float(z))
        n = renmas.maths.Vector3(float(nx), float(ny), float(nz))
        edge_a = renmas.maths.Vector3(float(eda_x), float(eda_y), float(eda_z))
        edge_b = renmas.maths.Vector3(float(edb_x), float(edb_y), float(edb_z))

        rect = renmas.shapes.Rectangle(p, edge_a, edge_b, n,  mat_idx)
        self.renderer.add_shape(name, rect)
        return rect

    def _create_mesh(self, props):
        mat_name = props.get("material", None)
        if mat_name is None: #logger
            mat_name = "default_material"
        mat_idx = self.renderer.material_index(mat_name)

        name = props.get("name", "Mesh" + str(renmas.utils.unique()))

        mesh = renmas.shapes.Mesh3D(mat_idx)

        fnames = props.get("resource", None)
        if fnames:
            for fname in fnames:
                mesh.load_mesh(fname)
        scale = props.get("scale", None)
        if scale:
            mesh.scale(scale[0], scale[1], scale[2])
            mesh.calculate_bbox()

        translate = props.get("translate", None)
        if translate:
            mesh.translate(translate[0], translate[1], translate[2])
            mesh.calculate_bbox()

        mesh.prepare_isect()

        self.renderer.add_shape(name, mesh)
        return mesh

    def create_material(self, props):
        name = props.get("name")
        sampling = props.get("sampling", "hemisphere_cos")

        mat = renmas.materials.Material()
        if sampling == "hemisphere_cos":
            sam = renmas.materials.HemisphereCos()
            mat.add_sampling(sam)
        elif sampling == "specular":
            sam = renmas.materials.SpecularSampling()
            mat.add_sampling(sam)
        else:
            raise ValueError("Sampling doesn't exist") #logger

        self.renderer.add_material(name, mat)
        return mat

    def add_brdf(self, material_name, props):
        # props is dict with properties
        brdf_name = props.get("type", "")
        mat = self.renderer.material(material_name)
        if mat is None: return

        if brdf_name == "lambertian":
            #he has reflectence properties for three channels
            r, g, b = props["R"]
            k = props.get("k", None)
            spectrum = renmas.core.Spectrum(float(r), float(g), float(b))
            lamb = renmas.materials.LambertianBRDF(spectrum, k)
            mat.add_component(lamb)
        elif brdf_name == "specular":
            #he has reflectence properties for three channels
            R = props["R"]
            spec = renmas.materials.SpecularBRDF(float(R))
            mat.add_component(spec)
        elif brdf_name == "constant":
            r, g, b = props["R"]
            k = props.get("k", None)
            spectrum = renmas.core.Spectrum(float(r), float(g), float(b))
            c = renmas.materials.ConstantBRDF(spectrum, k)
            mat.add_component(c)
        elif brdf_name == "phong":
            r, g, b = props["R"]
            e = props["e"]
            k = props.get("k", None)
            spectrum = renmas.core.Spectrum(float(r), float(g), float(b))
            c = renmas.materials.PhongBRDF(spectrum, float(e), k)
            mat.add_component(c)
        elif brdf_name == "oren_nayar":
            r, g, b = props["R"]
            alpha = float(props["alpha"])
            k = props.get("k", None)
            spectrum = renmas.core.Spectrum(float(r), float(g), float(b))
            c = renmas.materials.OrenNayarBRDF(spectrum, alpha, k)
            mat.add_component(c)
        elif brdf_name == "cook_torrance":
            r, g, b = props["R"]
            k = props.get("k", None)
            spectrum = renmas.core.Spectrum(float(r), float(g), float(b))
            if props["distribution"] == "gaussian":
                pr = props["dist_props"]
                c = float(pr["c"])
                m = float(pr["m"])
                dis = renmas.materials.GaussianDistribution(c, m)
            elif props["distribution"] == "beckmann":
                pr = props["dist_props"]
                m = float(pr["m"])
                dis = renmas.materials.BeckmannDistribution(m)
            else:
                raise ValueError("unknown distribution")
            comp = renmas.materials.CookTorranceBRDF(spectrum, dis, k)
            mat.add_component(comp)
        else:
            raise ValueError("unknown brdf name")


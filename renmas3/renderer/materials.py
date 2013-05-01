import math
from .surface import SurfaceShader

def create_lambertian_brdf(col_mgr, diffuse):
    diffuse = diffuse * (1.0 / math.pi) 
    code = """
shadepoint.material_reflectance = diffuse
    """
    props = {'diffuse': diffuse}
    bs = SurfaceShader(code, props, col_mgr=col_mgr)
    return bs

def create_lambertian_sample(col_mgr):
    code = """
sample = sample_hemisphere()
w = hitpoint.normal 
tv = (0.0034, 1.0, 0.0071)
v = cross(tv, w)
v = normalize(v)
u = cross(v, w)
ndir = u * sample[0] + v * sample[1] + w * sample[2]
shadepoint.wi = normalize(ndir)
    """
    props = {}
    bs = SurfaceShader(code, props, col_mgr=col_mgr)
    return bs

def create_lambertian_pdf(col_mgr):
    code = """
shadepoint.pdf = dot(hitpoint.normal, shadepoint.wi) * 0.318309886
    """
    props = {}
    bs = SurfaceShader(code, props, col_mgr=col_mgr)
    return bs

def create_lambertian_emission(col_mgr, emission_spectrum):
    code = """
shadepoint.material_emission = emission_spectrum
    """
    props = {'emission_spectrum': emission_spectrum}
    bs = SurfaceShader(code, props, col_mgr=col_mgr)
    return bs

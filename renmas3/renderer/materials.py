
from .surface import SurfaceShader

def create_lambertian_brdf(col_mgr, diffuse):
    code = """
shadepoint.material_spectrum = diffuse
    """
    props = {'diffuse': diffuse}
    bs = SurfaceShader(code, props, col_mgr=col_mgr)
    return bs

def create_lambertian_pdf():
    raise ValueError("Not yet implemented!")



from .surface import SurfaceShader

def create_point_illuminate(col_mgr, position, intesity):
        code = """
wi = position - hitpoint.hit

shadepoint.light_intensity = intesity
shadepoint.light_position = position
shadepoint.wi = normalize(wi)
        """
        props = {'position': position, 'intesity': intesity}
        bs = SurfaceShader(code, props, col_mgr=col_mgr)
        return bs


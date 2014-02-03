
from sdl import RGBSpectrum, SampledSpectrum, Shader,\
    RGBArg, SampledArg, FloatArg
from sdl.args import SampledArgPtr


def lum_sampled_shader(col_mgr):
    code = """
y =  cie_y * spec
y_sum = sum_samples(y)
return y_sum * scale
    """

    spec = col_mgr.zero()
    spec_arg = SampledArgPtr('spec', 0, spec)

    scale = (col_mgr.end - col_mgr.start) / (col_mgr.yint * col_mgr.nsamples)
    p1 = FloatArg('scale', scale)
    cie_y = SampledArg('cie_y', col_mgr._cie_y)

    shader = Shader(code=code, args=[p1, cie_y], name='lumminance',
                    func_args=[spec_arg], is_func=True)
    return shader


def lum_rgb_shader():
    code = """
return rgb[0] * 0.212671 + rgb[1] * 0.715160 + rgb[2] * 0.072169
    """
    rgb = RGBArg('rgb', RGBSpectrum(0.0, 0.0, 0.0))
    shader = Shader(code=code, name='lumminance',
                    func_args=[rgb], is_func=True)
    return shader


def rgb_to_vec_shader():
    code = """
return float3(rgb[0], rgb[1], rgb[2])
    """
    rgb = RGBArg('rgb', RGBSpectrum(0.0, 0.0, 0.0))
    shader = Shader(code=code, name='spectrum_to_vec',
                    func_args=[rgb], is_func=True)
    return shader


def sampled_to_vec_shader(col_mgr):
    code = """
x = cie_x * spec
y = cie_y * spec
z = cie_z * spec

X = sum_samples(x) * scale
Y = sum_samples(y) * scale
Z = sum_samples(z) * scale

r = 3.240479 * X - 1.537150 * Y - 0.498535 * Z
g = -0.969256 * X + 1.875991 * Y + 0.041556 * Z
b = 0.055648 * X - 0.204043 * Y + 1.057311 * Z

return float3(r, g, b)
    """

    spec = col_mgr.zero()
    spec_arg = SampledArgPtr('spec', 0, spec)

    scale = float(col_mgr.end - col_mgr.start) / (col_mgr.yint * col_mgr.nsamples)
    p1 = FloatArg('scale', scale)
    cie_x = SampledArg('cie_x', col_mgr._cie_x)
    cie_y = SampledArg('cie_y', col_mgr._cie_y)
    cie_z = SampledArg('cie_z', col_mgr._cie_z)

    shader = Shader(code=code, args=[p1, cie_x, cie_y, cie_z],
                    name='spectrum_to_vec',
                    func_args=[spec_arg], is_func=True)
    return shader



from sdl import RGBSpectrum, Shader, RGBArg, SampledArg,\
    FloatArg, Vec3Arg, Vector3, RGBManager, SampledManager
from sdl.args import SampledArgPtr


def _sampled_luminance_shader(sampled_mgr):
    code = """
y =  cie_y * spec
y_sum = sum_samples(y)
return y_sum * scale
    """
    spec = sampled_mgr.zero()
    spec_arg = SampledArgPtr('spec', 0, spec)

    scale = (sampled_mgr.end - sampled_mgr.start) / (sampled_mgr.yint * sampled_mgr.nsamples)
    p1 = FloatArg('scale', scale)
    cie_y = SampledArg('cie_y', sampled_mgr._cie_y)

    shader = Shader(code=code, args=[p1, cie_y], name='luminance',
                    func_args=[spec_arg], is_func=True)
    return shader


def _rgb_luminance_shader(rgb_mgr):
    code = """
return rgb[0] * 0.212671 + rgb[1] * 0.715160 + rgb[2] * 0.072169
    """
    rgb = RGBArg('rgb', RGBSpectrum(0.0, 0.0, 0.0))
    shader = Shader(code=code, name='luminance',
                    func_args=[rgb], is_func=True)
    return shader


def luminance_shader(color_mgr):
    if isinstance(color_mgr, RGBManager):
        return _rgb_luminance_shader(color_mgr)
    elif isinstance(color_mgr, SampledManager):
        return _sampled_luminance_shader(color_mgr)
    else:
        raise ValueError("Unsuported color manager! ", color_mgr)


def _rgb_to_rgb_shader(rgb_mgr):
    code = """
return float3(rgb[0], rgb[1], rgb[2])
    """
    rgb = RGBArg('rgb', RGBSpectrum(0.0, 0.0, 0.0))
    shader = Shader(code=code, name='spectrum_to_rgb',
                    func_args=[rgb], is_func=True)
    return shader


def _sampled_to_rgb_shader(sampled_mgr):
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

    spec = sampled_mgr.zero()
    spec_arg = SampledArgPtr('spec', 0, spec)

    scale = (sampled_mgr.end - sampled_mgr.start) / (sampled_mgr.yint * sampled_mgr.nsamples)
    p1 = FloatArg('scale', scale)
    cie_x = SampledArg('cie_x', sampled_mgr._cie_x)
    cie_y = SampledArg('cie_y', sampled_mgr._cie_y)
    cie_z = SampledArg('cie_z', sampled_mgr._cie_z)

    shader = Shader(code=code, args=[p1, cie_x, cie_y, cie_z],
                    name='spectrum_to_rgb',
                    func_args=[spec_arg], is_func=True)
    return shader


def spectrum_to_rgb_shader(color_mgr):
    if isinstance(color_mgr, RGBManager):
        return _rgb_to_rgb_shader(color_mgr)
    elif isinstance(color_mgr, SampledManager):
        return _sampled_to_rgb_shader(color_mgr)
    else:
        raise ValueError("Unsuported color manager! ", color_mgr)


def _rgb_to_rgb_spectrum_shader(rgb_mgr):
    code = """
return rgb(color[0], color[1], color[2])
    """
    vec = Vec3Arg('color', Vector3.zero())
    shader = Shader(code=code, name='rgb_to_spectrum',
                    func_args=[vec], is_func=True)
    return shader


def _rgb_to_sampled_shader(sampled_mgr):
    code = """
# conversion of reflectance
r = color[0]
g = color[1]
b = color[2]

tmp = min(r, g)
tmp = min(tmp, b)
if tmp == r:
    # Compute illuminant with red as minimum
    rez = r * spect_white
    if g > b:
        rez = rez + (b - r) * spect_cyan
        rez = rez + (g - b) * spect_green
    else:
        rez = rez + (g - r) * spect_cyan
        rez = rez + (b - g) * spect_blue
else:
    dummy = 999999 # elif is still not supported in shading language
    if tmp == g:
        # Compute illuminant with green as minimum
        rez = g * spect_white
        if r > b:
            rez = rez + (b - g) * spect_magenta
            rez = rez + (r - b) * spect_red
        else:
            rez = rez + (r - g) * spect_magenta
            rez = rez + (b - r) * spect_blue
    else:
        # Compute illuminant with blue as minimum
        rez = b * spect_white
        if r > g:
            rez = rez + (g - b) * spect_yellow
            rez = rez + (r - g) * spect_red
        else:
            rez = rez + (r - b) * spect_yellow
            rez = rez + (g - r) * spect_green

rez = rez * 0.94
#rez.clamp()
return rez
    """

    vec = Vec3Arg('color', Vector3.zero())

    spect_cyan = SampledArg('spect_cyan', sampled_mgr._spect_cyan)
    spect_blue = SampledArg('spect_blue', sampled_mgr._spect_blue)
    spect_green = SampledArg('spect_green', sampled_mgr._spect_green)
    spect_magenta = SampledArg('spect_magenta', sampled_mgr._spect_magenta)
    spect_red = SampledArg('spect_red', sampled_mgr._spect_red)
    spect_yellow = SampledArg('spect_yellow', sampled_mgr._spect_yellow)
    spect_white = SampledArg('spect_white', sampled_mgr._spect_white)

    args = [spect_cyan, spect_blue, spect_green, spect_magenta,
            spect_red, spect_yellow, spect_white]

    shader = Shader(code=code, args=args,
                    name='rgb_to_spectrum',
                    func_args=[vec], is_func=True)
    return shader


def rgb_to_spectrum_shader(color_mgr):
    if isinstance(color_mgr, RGBManager):
        return _rgb_to_rgb_spectrum_shader(color_mgr)
    elif isinstance(color_mgr, SampledManager):
        return _rgb_to_sampled_shader(color_mgr)
    else:
        raise ValueError("Unsuported color manager! ", color_mgr)

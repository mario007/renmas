
from functools import partial
from sdl import FloatArg, Vec3Arg, Vec4Arg, RGBArg, RGBSpectrum,\
    StructArg, arg_from_value, Vector3, get_struct_desc, Vector4,\
    ImagePRGBA


def _parse_float(line):
    t = line.split('=', maxsplit=1)
    name = t.pop(0).strip()
    if len(t) == 0:
        return FloatArg(name, 0.0)
    v = float(t.pop(0).strip())
    return FloatArg(name, v)


def _parse_vec4(line):
    t = line.split('=', maxsplit=1)
    name = t.pop(0).strip()
    if len(t) == 0:
        return Vec4Arg(name, Vector4(0.0, 0.0, 0.0, 0.0))

    v = t.pop(0).strip().split(',')
    arg = Vec4Arg(name, Vector4(float(v[0]), float(v[1]),
                                float(v[2]), float(v[3])))

    return arg


def _parse_vec3(line):
    t = line.split('=', maxsplit=1)
    name = t.pop(0).strip()
    if len(t) == 0:
        return Vec3Arg(name, Vector3(0.0, 0.0, 0.0))

    v = t.pop(0).strip().split(',')
    arg = Vec3Arg(name, Vector3(float(v[0]), float(v[1]),
                                float(v[2])))
    return arg


def _parse_rgb(line, color_mgr=None):
    t = line.split('=', maxsplit=1)
    name = t.pop(0).strip()
    if len(t) == 0:
        if color_mgr is None:
            return RGBArg(name, RGBSpectrum(0.0, 0.0, 0.0))
        else:
            return arg_from_value(name, color_mgr.zero())
    v = t.pop(0).strip().split(',')
    spectrum = RGBSpectrum(float(v[0]), float(v[1]), float(v[2]))
    if color_mgr is None:
        return RGBArg(name, spectrum)
    else:
        return arg_from_value(name, color_mgr.convert_spectrum(spectrum))


def _parse_image(line, image_factory=None):
    if image_factory is None:
        img = ImagePRGBA(1, 1)  # image of 1 pixel in size
    else:
        img = image_factory()
    name = line
    arg = StructArg(name, img)
    return arg


def parse_args(text, color_mgr=None, image_factory=None):
    _new_parse_rgb = partial(_parse_rgb, color_mgr=color_mgr)
    _new_parse_image = partial(_parse_image, image_factory=image_factory)

    funcs = {'vector4': _parse_vec4, 'rgb': _new_parse_rgb,
             'float': _parse_float, 'vector3': _parse_vec3,
             'image': _new_parse_image}

    args = []
    for line in text.splitlines():
        line = line.strip()
        if line == '':
            continue
        type_name, rest = line.split(maxsplit=1)
        desc = get_struct_desc(type_name=type_name)
        if type_name in funcs:
            arg = funcs[type_name](rest.strip())
        elif desc is not None:
            value = desc.factory()
            vals = rest.strip().split()
            name = vals.pop(0).strip()
            arg = StructArg(name, value)
        else:
            raise ValueError("Unknown typename ", type_name)
        args.append(arg)
    return args

from ..base import ImagePRGBA, BasicShader
from tdasm import Runtime

class Tmo:
    def __init__(self, code, props):

        if 'input_image' in props:
            raise ValueError("input_image property allready exist in tone mapping props")
        if 'output_image' in props:
            raise ValueError("output_image property allready exist in tone mapping props")
        props['input_image'] = ImagePRGBA
        props['output_image'] = ImagePRGBA

        self._tmo = BasicShader(code, props)
        self._tmo.prepare([Runtime()])
    
    def get_props(self):
        return self._tmo.props

    def get_prop(self, name):
        return self._tmo.shader.get_value(name)

    def set_prop(self, name, prop):
        self._tmo.shader.set_value(name, prop)

    def tone_map(self, input_image, output_image):
        if not isinstance(input_image, ImagePRGBA):
            raise ValueError("Input type of image is expected to be instance of ImagePRGBA")
        if not isinstance(output_image, ImagePRGBA):
            raise ValueError("Output type of image is expected to be instance of ImagePRGBA")
        width, height = input_image.size()
        out_width, out_height = output_image.size()
        if width != out_width or height != out_height:
            raise ValueError("Input and output image must be of the same size!",
                    width, out_width, height, out_height)

        self._tmo.shader.set_value('input_image', input_image)
        self._tmo.shader.set_value('output_image', output_image)
        self._tmo.execute()

class ToneMapping:
    def __init__(self):
        pass

    def tone_map(self, hdr_image, ldr_image):
        raise NotImplementedError()


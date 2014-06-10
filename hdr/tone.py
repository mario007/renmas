
import os.path
from tdasm import Runtime
from sdl import Loader, Shader, ImagePRGBA, StructArg
from .parse_args import parse_args


class Tmo:
    def __init__(self):
        path = os.path.dirname(__file__)
        path = os.path.join(path, 'shaders')
        self._loader = Loader([path])

        self._shader = None
        self._runtime = None

    @property
    def shader(self):
        return self._shader

    def load(self, name):
        props = self._loader.load(name, 'props.txt')
        args = []
        if props is not None:
            args = parse_args(props)

        in_img = StructArg('input_image', ImagePRGBA(1, 1))
        out_img = StructArg('output_image', ImagePRGBA(1, 1))
        args.extend([in_img, out_img])

        code = self._loader.load(name, 'code.py')
        self._shader = Shader(code=code, args=args)
        self._shader.compile()
        self._runtime = Runtime()
        self._shader.prepare([self._runtime])

    def tmo(self, in_img, out_img):
        """
            Perform tone mapping on input image

            Args:
                in_img:  Input image
                out_img: Output image

        """
        if self._shader is None:
            raise ValueError("Shader is not loaded.")

        if not isinstance(in_img, ImagePRGBA) and not isinstance(out_img, ImagePRGBA):
            raise ValueError("ImagePRGBA is expected insted of", in_img, out_img)

        w1, h1 = in_img.size()
        w2, h2 = out_img.size()
        if w1 != w2 or h1 != h2:
            raise ValueError("Input and output image must be same size!")

        self._shader.set_value('input_image', in_img)
        self._shader.set_value('output_image', out_img)
        self._shader.execute()

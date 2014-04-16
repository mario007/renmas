"""
    This module contain implementation of classes that store image.
"""

import platform
import x86
from tdasm import Tdasm, Runtime


def _conv_rgba_bgra_asm32():
    ASM = """
    #DATA
    uint32 ptr_src, ptr_dst
    uint32 npixels
    #CODE
    mov esi, dword [ptr_src]
    mov edi, dword [ptr_dst]
    mov ebp, dword [npixels]

    _loop:
    mov eax, dword [esi]
    bswap eax
    ror eax, 8
    mov dword [edi], eax

    add esi, 4
    add edi, 4
    sub ebp, 1
    jnz _loop
    #END
    """
    return ASM


def _conv_rgba_bgra_asm64():
    ASM = """
    #DATA
    uint64 ptr_src, ptr_dst
    uint32 npixels
    #CODE
    mov rsi, qword [ptr_src]
    mov rdi, qword [ptr_dst]
    mov ebp, dword [npixels]

    _loop:
    mov eax, dword [rsi]
    bswap eax
    ror eax, 8
    mov dword [rdi], eax

    add rsi, 4
    add rdi, 4
    sub ebp, 1
    jnz _loop
    #END
    """
    return ASM


def _conv_rgba_bgra_asm():
    bits = platform.architecture()[0]
    if bits == '64bit':
        code = _conv_rgba_bgra_asm64()
        mc = Tdasm().assemble(code, ia32=False)
    else:
        code = _conv_rgba_bgra_asm32()
        mc = Tdasm().assemble(code, ia32=True)

    runtime = Runtime()
    ds = runtime.load("convert", mc)
    return runtime, ds

_runtime, _ds = _conv_rgba_bgra_asm()


def _convert_pixels(npixels, src, dst):
    _ds['npixels'] = npixels
    _ds['ptr_src'] = src
    _ds['ptr_dst'] = dst
    _runtime.run('convert')


class Image:
    """
        Base Image class that holds dimension of image and pixels.
        You don't have to instantiate this class directly, use
        more specialized version.
    """
    def __init__(self, width, height, pitch):
        """
            Create image with specified width and height.
            Also pitch is required that represent number of bytes in raw.
        """
        self.pitch = pitch
        self.width = width
        self.height = height
        self._pixels = x86.MemData(height * pitch)

    @property
    def pixels(self):
        """
            Return address of pixels
        """
        return self._pixels.ptr()

    def size(self):
        """
            Return size of image. (width, height) tuple is returned.
        """
        return (self.width, self.height)

    def address_info(self):
        """
            Return pixels and pitch. (pixels, pitch) tuple is returned.
        """
        return (self._pixels.ptr(), self.pitch)

    def clear(self):
        """
            Fill image with zeroes.
        """
        self._pixels.fill()

    def __repr__(self):
        """
           Return information about image.
        """
        adr = self._pixels.ptr()
        return '<Image object at %s Width=%i, Height=%i, Pitch=%i, Pixels=%s>' % \
                (hex(id(self)), self.width, self.height, self.pitch, hex(adr))


class ImageRGBA(Image):
    """
        Image class that stores pixels in rgba format.
        For each component (red, green, blue, alpha) 8 bits are used.
    """
    def __init__(self, width, height):
        """
            Create image of specified width and height in rgba format.
        """
        super(ImageRGBA, self).__init__(width, height, width*4)

    def set_pixel(self, x, y, r, g, b, a=255):
        """
            Set color of pixel at cooridantes x, y.
            r, g, b, a are red, green blue and alpha color components.
            Each component must be in range 0-255.
            Default value for alpha component is 255.
            Function return False if x, y coordinates are out of
            range otherwise True
        """
        if x < 0 or x >= self.width:
            return False
        if y < 0 or y >= self.height:
            return False
        adr = y * self.pitch + x * 4
        pix = (a<<24) | (b<<16) | (g<<8) | r
        x86.SetUInt32(self._pixels.ptr() + adr, pix, 0)
        return True

    def get_pixel(self, x, y):
        """
            Get color of pixel at cooridantes x, y. (r, g, b, a) tuple is returned.
            If x, y cooridantes are out of range None is return.
        """
        if x < 0 or x >= self.width:
            return None
        if y < 0 or y >= self.height:
            return None
        adr = y * self.pitch + x * 4
        pix = x86.GetUInt32(self._pixels.ptr() + adr, 0, 0)
        r = pix & 0xFF
        g = (pix >> 8) & 0xFF
        b = (pix >> 16) & 0xFF
        a = pix >> 24
        return (r, g, b, a)

    def to_bgra(self):
        """
            Create copy of this image in bgra format.
            New image in brga format is returned.
        """
        img = ImageBGRA(self.width, self.height)
        src, pitch = self.address_info()
        dst, pitch = img.address_info()
        _convert_pixels(self.width*self.height, src, dst)
        return img

    def __repr__(self):
        """
           Return information about image.
        """
        adr = self._pixels.ptr()
        return '<ImageRGBA object at %s Width=%i, Height=%i, Pitch=%i, Pixels=%s>' % \
                (hex(id(self)), self.width, self.height, self.pitch, hex(adr))


class ImageBGRA(Image):
    """
        Image class that stores pixels in bgra format.
        For each component (red, green, blue, alpha) 8 bits are used.
        This format is usually used in windows for display.
    """
    def __init__(self, width, height):
        """
            Create image of specified width and height in bgra format.
        """
        super(ImageBGRA, self).__init__(width, height, width*4)

    def set_pixel(self, x, y, r, g, b, a=255):
        """
            Set color of pixel at cooridantes x, y.
            r, g, b, a are red, green blue and alpha color components.
            Each component must be in range 0-255.
            Default value for alpha component is 255.
            Function return False if x, y coordinates are out of range
            otherwise True
        """
        if x < 0 or x >= self.width:
            return False
        if y < 0 or y >= self.height:
            return False
        adr = y * self.pitch + x * 4
        pix = (a<<24) | (r<<16) | (g<<8) | b
        x86.SetUInt32(self._pixels.ptr() + adr, pix, 0)
        return True

    def get_pixel(self, x, y):
        """
            Get color of pixel at cooridantes x, y. (r, g, b, a) tuple is returned.
            If x, y cooridantes are out of range None is return.
        """
        if x < 0 or x >= self.width:
            return None
        if y < 0 or y >= self.height:
            return None
        adr = y * self.pitch + x * 4
        pix = x86.GetUInt32(self._pixels.ptr() + adr, 0, 0)
        b = pix & 0xFF
        g = (pix >> 8) & 0xFF
        r = (pix >> 16) & 0xFF
        a = pix >> 24
        return (r, g, b, a)

    def to_rgba(self):
        """
            Create copy of this image in rgba format.
            New image in rgba format is returned.
        """
        img = ImageRGBA(self.width, self.height)
        src, pitch = self.address_info()
        dst, pitch = img.address_info()
        _convert_pixels(self.width*self.height, src, dst)
        return img

    def __repr__(self):
        """
           Return information about image.
        """
        adr = self._pixels.ptr()
        return '<ImageBGRA object at %s Width=%i, Height=%i, Pitch=%i, Pixels=%s>' % \
                (hex(id(self)), self.width, self.height, self.pitch, hex(adr))


class ImagePRGBA(Image):
    """
        Image class that stores pixels in rgba format.
        Each component (red, green, blue and alpa) uses 32 bits
        and are written in floating-point format.

    """

    def __init__(self, width, height):
        """
            Create image of specified width and height in prgba format.
        """
        super(ImagePRGBA, self).__init__(width, height, width*16)

    def set_pixel(self, x, y, r, g, b, a=0.99):
        """
            Set color of pixel at cooridantes x, y.
            r, g, b, a are red, green blue and alpha color components.
            Default value for alpha component is 0.99.
            Function return False if x, y coordinates are out of
            range otherwise True
        """
        if x < 0 or x >= self.width:
            return False
        if y < 0 or y >= self.height:
            return False
        adr = y * self.pitch + x * 16
        x86.SetFloat(self._pixels.ptr() + adr, (r, g, b, a), 0)
        return True

    def get_pixel(self, x, y):
        """
            Get color of pixel at cooridantes x, y. (r, g, b, a)
            tuple is returned.
            If x, y cooridantes are out of range None is return.
        """
        if x < 0 or x >= self.width:
            return None
        if y < 0 or y >= self.height:
            return None
        adr = y * self.pitch + x * 16
        # return r, g, b, a
        return x86.GetFloat(self._pixels.ptr() + adr, 0, 4)

    def __repr__(self):
        """
           Return information about image.
        """
        adr = self._pixels.ptr()
        return '<ImagePRGBA object at %s Width=%i, Height=%i, Pitch=%i, Pixels=%s>' % \
                (hex(id(self)), self.width, self.height, self.pitch, hex(adr))


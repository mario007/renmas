
import platform
import x86
from tdasm import Tdasm, Runtime

#TODO - 64bit implementation
def _conv_rgba_bgra_asm():
    ASM = """
    #DATA
    uint32 ptr_src, ptr_dst
    uint32 npixels
    #CODE
    mov esi, dword [ptr_src]
    mov edi, dword [ptr_dst]
    mov ebp, dword [npixels]

    _loop:
    mov al, byte [esi]
    mov bl, byte [esi+1]
    mov cl, byte [esi+2]
    mov dl, byte [esi+3]

    mov byte [edi], cl
    mov byte [edi+1], bl
    mov byte [edi+2], al
    mov byte [edi+3], dl

    add esi, 4 
    add edi, 4 
    sub ebp, 1
    jnz _loop
    #END
    """
    mc = Tdasm().assemble(ASM)
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
    def __init__(self, width, height, pitch):
        self.pitch = pitch
        self.width = width
        self.height = height
        self.pixels = x86.MemData(height * pitch)

    def set_pixel(self, x, y, r, g, b, a):
        raise NotImplementedError()

    def get_pixel(self, x, y):
        raise NotImplementedError()

    def size(self):
        return (self.width, self.height)

    def address_info(self):
        return (self.pixels.ptr(), self.pitch)

    def __repr__(self):
        adr = self.pixels.ptr()
        return '<Image object at %s Width=%i, Height=%i, Pitch=%i, Pixels=%s>' % \
                (hex(id(self)), self.width, self.height, self.pitch, hex(adr))

class ImageRGBA(Image):
    def __init__(self, width, height):
        super(ImageRGBA, self).__init__(width, height, width*4)
        
    def set_pixel(self, x, y, r, g, b, a=255):
        if x < 0 or x >= self.width: return
        if y < 0 or y >= self.height: return
        adr = y * self.pitch + x * 4
        pix = (a<<24) | (b<<16) | (g<<8) | r
        x86.SetUInt32(self.pixels.ptr()+adr, pix, 0)

    def get_pixel(self, x, y):
        if x < 0 or x >= self.width: return None
        if y < 0 or y >= self.height: return None
        adr = y * self.pitch + x * 4
        pix = x86.GetUInt32(self.pixels.ptr()+adr, 0, 0)
        r = pix & 0xFF
        g = (pix >> 8) & 0xFF
        b = (pix >> 16) & 0xFF
        a = pix >> 24
        return (r, g, b, a) 

    def to_bgra(self):
        img = ImageBGRA(self.width, self.height)
        src, pitch = self.address_info()
        dst, pitch = img.address_info()
        _convert_pixels(self.width*self.height, src, dst)
        return img

    def __repr__(self):
        adr = self.pixels.ptr()
        return '<ImageRGBA object at %s Width=%i, Height=%i, Pitch=%i, Pixels=%s>' % \
                (hex(id(self)), self.width, self.height, self.pitch, hex(adr))

class ImageBGRA(Image):
    def __init__(self, width, height):
        super(ImageBGRA, self).__init__(width, height, width*4)

    def set_pixel(self, x, y, r, g, b, a=255):
        if x < 0 or x >= self.width: return
        if y < 0 or y >= self.height: return
        adr = y * self.pitch + x * 4
        pix = (a<<24) | (r<<16) | (g<<8) | b
        x86.SetUInt32(self.pixels.ptr()+adr, pix, 0)

    def get_pixel(self, x, y):
        if x < 0 or x >= self.width: return None
        if y < 0 or y >= self.height: return None
        adr = y * self.pitch + x * 4
        pix = x86.GetUInt32(self.pixels.ptr()+adr, 0, 0)
        b = pix & 0xFF
        g = (pix >> 8) & 0xFF
        r = (pix >> 16) & 0xFF
        a = pix >> 24
        return (r, g, b, a) 

    def to_rgba(self):
        img = ImageRGBA(self.width, self.height)
        src, pitch = self.address_info()
        dst, pitch = img.address_info()
        _convert_pixels(self.width*self.height, src, dst)
        return img

    def __repr__(self):
        adr = self.pixels.ptr()
        return '<ImageBGRA object at %s Width=%i, Height=%i, Pitch=%i, Pixels=%s>' % \
                (hex(id(self)), self.width, self.height, self.pitch, hex(adr))

class ImageFloatRGBA(Image):
    def __init__(self, width, height):
        super(ImageFloatRGBA, self).__init__(width, height, width*16)

    def set_pixel(self, x, y, r, g, b, a=0.99):
        if x < 0 or x >= self.width: 
            raise ValueError("Out of bounds:x=" + str(x) + " y=" + str(y) + " width=" + str(self.width) + " height=" + str(self.height))
        if y < 0 or y >= self.height: 
            raise ValueError("Out of bounds:x=" + str(x) + " y=" + str(y) + " width=" + str(self.width) + " height=" + str(self.height))
        adr = y * self.pitch + x * 16

        x86.SetFloat(self.pixels.ptr()+adr, (r, g, b, a), 0)

    def get_pixel(self, x, y):
        if x < 0 or x >= self.width: return None
        if y < 0 or y >= self.height: return None
        adr = y * self.pitch + x * 16
        # return r, g, b, a 
        pix = x86.GetFloat(self.pixels.ptr()+adr, 0, 4)
        return pix


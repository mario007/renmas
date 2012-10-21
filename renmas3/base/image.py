
import platform
import x86
from tdasm import Tdasm, Runtime

from .arg import Integer, Pointer
from .cgen import register_user_type

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
    else:
        code =  _conv_rgba_bgra_asm32()

    mc = Tdasm().assemble(code)
    runtime = Runtime()
    ds = runtime.load("convert", mc)
    return runtime, ds

_runtime, _ds = _conv_rgba_bgra_asm()

def _convert_pixels(npixels, src, dst):
    _ds['npixels'] = npixels
    _ds['ptr_src'] = src
    _ds['ptr_dst'] = dst 
    _runtime.run('convert')

## Base image class. 
# Image
class Image:
    ## Constructor.
    # Create Image of specified width, height.  
    # You also must specifies number of bytes in one row. It is usually called pitch.
    # @param self The object pointer
    # @param width Width of the image
    # @param height Height of the image
    # @param pitch Pitch of the image
    def __init__(self, width, height, pitch):
        self.pitch = pitch
        self.width = width
        self.height = height
        self.pixels = x86.MemData(height * pitch)

    ## Return size of image  
    # @param self The object pointer
    # @return Return width x height of image 
    def size(self):
        return (self.width, self.height)

    ## Return address of pixels and pitch  
    # @param self The object pointer
    # @return Return adrress, pitch of image 
    def address_info(self):
        return (self.pixels.ptr(), self.pitch)

    def __repr__(self):
        adr = self.pixels.ptr()
        return '<Image object at %s Width=%i, Height=%i, Pitch=%i, Pixels=%s>' % \
                (hex(id(self)), self.width, self.height, self.pitch, hex(adr))

## Main image class for holding images, textures. 
# Pixels is represented in rgba format.  
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

## Main image class for display.
# WindowsGDI wants that pixels are in bgra format!!!. 
# Because of that this class is used as frame buffer.
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
        self.pixels_ptr = self.pixels.ptr()

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

    
    @staticmethod
    def struct():
        typ_name = "ImageFloatRGBA"
        fields = [('width', Integer), ('height', Integer), ('pitch', Integer), ('pixels_ptr', Pointer)]
        return (typ_name, fields)

    def __repr__(self):
        adr = self.pixels.ptr()
        return '<ImageFloatRGBA object at %s Width=%i, Height=%i, Pitch=%i, Pixels=%s>' % \
                (hex(id(self)), self.width, self.height, self.pitch, hex(adr))

register_user_type(ImageFloatRGBA)

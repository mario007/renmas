
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
    ## Create Image of specified width, height.  
    # You also must specifies number of bytes in one row. It is usually called pitch.
    # @param self The object pointer
    # @param width Width of the image
    # @param height Height of the image
    # @param pitch Pitch of the image
    def __init__(self, width, height, pitch):
        ## @brief pitch of the image(number of bytes in row)
        self.pitch = pitch
        ## @brief width of the image
        self.width = width
        ## @brief height of the image
        self.height = height

        self._pixels = x86.MemData(height * pitch)

    ## Return address of pixel array 
    # @param self The object pointer
    # @return Return address of pixel array
    @property
    def pixels(self):
        return self._pixels.ptr()

    ## Return size of image  
    # @param self The object pointer
    # @return Return width x height of image 
    def size(self):
        return (self.width, self.height)

    ## Return address of pixel array and pitch  
    # @param self The object pointer
    # @return Return tuple (pixels, pitch)
    def address_info(self):
        return (self._pixels.ptr(), self.pitch)

    def __repr__(self):
        adr = self._pixels.ptr()
        return '<Image object at %s Width=%i, Height=%i, Pitch=%i, Pixels=%s>' % \
                (hex(id(self)), self.width, self.height, self.pitch, hex(adr))

## Image class that stores pixels in rgba format.
# For each component (red, green, blue, alpha) 8 bits are used.
class ImageRGBA(Image):
    ## Create Image of specified width, height.  
    # @param self The object pointer
    # @param width Width of the image
    # @param height Height of the image
    def __init__(self, width, height):
        super(ImageRGBA, self).__init__(width, height, width*4)
        
    ## Set color of pixel at cooridantes x, y.
    # @param self The object pointer
    # @param x x coordinate
    # @param y y coordiante
    # @param r red component in range 0-255
    # @param g green component in range 0-255
    # @param b blue component in range 0-255
    # @param a alpa component of the image in range 0-255. Default value is 255.
    # @return Return False if coordinates are out of range otherwise True
    def set_pixel(self, x, y, r, g, b, a=255):
        if x < 0 or x >= self.width:
            return False
        if y < 0 or y >= self.height:
            return False
        adr = y * self.pitch + x * 4
        pix = (a<<24) | (b<<16) | (g<<8) | r
        x86.SetUInt32(self._pixels.ptr()+adr, pix, 0)
        return True

    ## Get color of pixel at cooridantes x, y.
    # If cooridantes are out of range None is return.
    # @param self The object pointer
    # @param x x coordinate
    # @param y y coordiante
    # @return Return tuple (r, g, b, a)
    def get_pixel(self, x, y):
        if x < 0 or x >= self.width:
            return None
        if y < 0 or y >= self.height:
            return None
        adr = y * self.pitch + x * 4
        pix = x86.GetUInt32(self._pixels.ptr()+adr, 0, 0)
        r = pix & 0xFF
        g = (pix >> 8) & 0xFF
        b = (pix >> 16) & 0xFF
        a = pix >> 24
        return (r, g, b, a) 

    ## Create copy of this image in bgra format.
    # @param self The object pointer
    # @return Return image in brga format
    def to_bgra(self):
        img = ImageBGRA(self.width, self.height)
        src, pitch = self.address_info()
        dst, pitch = img.address_info()
        _convert_pixels(self.width*self.height, src, dst)
        return img

    def __repr__(self):
        adr = self._pixels.ptr()
        return '<ImageRGBA object at %s Width=%i, Height=%i, Pitch=%i, Pixels=%s>' % \
                (hex(id(self)), self.width, self.height, self.pitch, hex(adr))

## Image class that stores pixels in bgra format.
# For each component (blue, green, red, alpha) 8 bits are used.
class ImageBGRA(Image):
    def __init__(self, width, height):
        super(ImageBGRA, self).__init__(width, height, width*4)

    ## Set color of pixel at cooridantes x, y.
    # @param self The object pointer
    # @param x x coordinate
    # @param y y coordiante
    # @param r red component in range 0-255
    # @param g green component in range 0-255
    # @param b blue component in range 0-255
    # @param a alpa component of the image in range 0-255. Default value is 255.
    # @return Return False if coordinates are out of range otherwise True
    def set_pixel(self, x, y, r, g, b, a=255):
        if x < 0 or x >= self.width:
            return False
        if y < 0 or y >= self.height:
            return False
        adr = y * self.pitch + x * 4
        pix = (a<<24) | (r<<16) | (g<<8) | b
        x86.SetUInt32(self._pixels.ptr()+adr, pix, 0)
        return True

    ## Get color of pixel at cooridantes x, y.
    # If cooridinates are out of range None is return.
    # @param self The object pointer
    # @param x x coordinate
    # @param y y coordiante
    # @return Return tuple (r, g, b, a)
    def get_pixel(self, x, y):
        if x < 0 or x >= self.width:
            return None
        if y < 0 or y >= self.height:
            return None
        adr = y * self.pitch + x * 4
        pix = x86.GetUInt32(self._pixels.ptr()+adr, 0, 0)
        b = pix & 0xFF
        g = (pix >> 8) & 0xFF
        r = (pix >> 16) & 0xFF
        a = pix >> 24
        return (r, g, b, a) 

    ## Create copy of this image in rgba format.
    # @param self The object pointer
    # @return Return image in rgba format
    def to_rgba(self):
        img = ImageRGBA(self.width, self.height)
        src, pitch = self.address_info()
        dst, pitch = img.address_info()
        _convert_pixels(self.width*self.height, src, dst)
        return img

    def __repr__(self):
        adr = self._pixels.ptr()
        return '<ImageBGRA object at %s Width=%i, Height=%i, Pitch=%i, Pixels=%s>' % \
                (hex(id(self)), self.width, self.height, self.pitch, hex(adr))

## Image class that stores pixels in rgba format.
# For each component (red, green, blue, alpha) 32 bits are used.
class ImagePRGBA(Image):
    def __init__(self, width, height):
        super(ImagePRGBA, self).__init__(width, height, width*16)

    ## Set color of pixel at cooridantes x, y.
    # @param self The object pointer
    # @param x x coordinates
    # @param y y coordiantes
    # @param r red component in range 0.0-0.99
    # @param g green component in range 0.0-0.99
    # @param b blue component in range 0.0-0.99
    # @param a alpa component of the image in range 0.0-0.99. Default value is 0.99.
    # @return Return False if coordinates are out of range otherwise True
    def set_pixel(self, x, y, r, g, b, a=0.99):
        if x < 0 or x >= self.width: 
            return False
        if y < 0 or y >= self.height: 
            return False
        adr = y * self.pitch + x * 16
        x86.SetFloat(self._pixels.ptr()+adr, (r, g, b, a), 0)
        return True

    ## Get color of pixel at cooridantes x, y.
    # If cooridinates are out of range None is return.
    # @param self The object pointer
    # @param x x coordinate
    # @param y y coordiante
    # @return Return tuple (r, g, b, a)
    def get_pixel(self, x, y):
        if x < 0 or x >= self.width:
            return None
        if y < 0 or y >= self.height:
            return None
        adr = y * self.pitch + x * 16
        # return r, g, b, a 
        return x86.GetFloat(self._pixels.ptr()+adr, 0, 4)
    
    @classmethod
    def user_type(cls):
        typ_name = "ImagePRGBA"
        fields = [('width', Integer), ('height', Integer), ('pitch', Integer), ('pixels', Pointer)]
        return (typ_name, fields)

    def __repr__(self):
        adr = self._pixels.ptr()
        return '<ImagePRGBA object at %s Width=%i, Height=%i, Pitch=%i, Pixels=%s>' % \
                (hex(id(self)), self.width, self.height, self.pitch, hex(adr))

register_user_type(ImagePRGBA)

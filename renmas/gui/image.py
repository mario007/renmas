
import x86
from tdasm import Tdasm

#image in memory bgra - be cerful
#Image class with RGBA format
class ImageRGBA:
    def __init__(self, width, height):
        n = width * height * 4 
        self.pixels = x86.MemData(n)
        self.width = width
        self.height = height
        self.pitch = width * 4

    def set_pixel(self, x, y, r, g, b, a=255):
        #y = self.height - y - 1 # for flipping image
        #clipping FIXME throw exception
        if x < 0 or x >= self.width: return
        if y < 0 or y >= self.height: return
        adr = y * self.pitch + x * 4
        pix = (a<<24) | (r<<16) | (g<<8) | b
        x86.SetUInt32(self.pixels.ptr()+adr, pix, 0)

    def get_pixel(self, x, y):
        if x < 0 or x >= self.width: return None
        if y < 0 or y >= self.height: return None
        adr = y * self.width * 4 + x * 4
        # return b, g, r, a
        pix = x86.GetUInt32(self.pixels.ptr()+adr, 0, 0)
        return pix

    def get_addr(self):
        return (self.pixels.ptr(), self.pitch)

    def get_size(self):
        return (self.width, self.height)

#FIXME how to store float image data argb change to rgba
class ImageFloatRGBA:
    def __init__(self, width, height):
        n = width * height * 4 * 4 
        self.pixels = x86.MemData(n)
        self.width = width
        self.height = height
        self.pitch = width * 16

    def get_addr(self):
        return self.pixels.ptr(), self.pitch

    def get_size(self):
        return (self.width, self.height)

    def generate_asm(self, runtime, label):
        asm_code = """
        #DATA
        uint32 ptr_buffer
        uint32 pitch
        #CODE
        ; eax = x , ebx = y, value = xmm0
        """
        asm_code += "global " + label + ": \n"
        asm_code += """
        imul ebx, dword [pitch]
        imul eax , eax, 16
        mov ecx, dword [ptr_buffer]
        add eax, ebx
        add ecx, eax
        movaps oword [ecx], xmm0
        ret
        """
        asm = Tdasm()
        mc = asm.assemble(asm_code, True)
        name = "ImageFloatRGBA" 
        self.ds = runtime.load(name, mc)
        self.ds["ptr_buffer"] = self.pixels.ptr()
        self.ds["pitch"] = self.pitch

    def set_pixel(self, x, y, r, g, b, a=0.99):
        #y = self.height - y - 1 # for flipping image

        #clipping 
        if x < 0 or x >= self.width: return
        if y < 0 or y >= self.height: return
        adr = y * self.pitch + x * 16

        x86.SetFloat(self.pixels.ptr()+adr, (r, g, b, a), 0)

    def get_pixel(self, x, y):
        if x < 0 or x >= self.width: return None
        if y < 0 or y >= self.height: return None
        adr = y * self.pitch + x * 16
        # return b, g, r, a
        pix = x86.GetFloat(self.pixels.ptr()+adr, 0, 4)
        return pix


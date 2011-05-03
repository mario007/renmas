
from tdasm import Tdasm, Runtime

#TODO 64-bit for address
ASM_STR = """
    #DATA
    uint32 address
    uint32 x, y, width, height
    uint32 color
    uint32 pitch

    #CODE
    call set_pixel

    #END
    
    set_pixel:
    mov eax, dword [y]
    mul dword [pitch]
    mov edx, dword [x]
    imul edx, edx, 4
    
    add eax, edx 
    add eax, dword [address]
    mov ebx, dword [color]
    mov dword [eax], ebx  
    ret
"""

# for now just rgba
#BGRA Format - Little endian - windows implementation 
# TODO make utility functions for colors
#FIXME For know we don't check if pixel is out of bounds!!!
class Graphic2D:
    def __init__(self, width, height, pitch, address):
        self.addr = address
        self.width = width
        self.height = height
        asm = Tdasm()
        m = asm.assemble(ASM_STR)
        self.r = Runtime()
        self.ds = self.r.load("set_pixel", m)
        self.ds["color"] = 0xFF00FF00 # red color is default
        self.ds["address"] = address
        self.ds["width"] = width
        self.ds["height"] = height
        self.ds["pitch"] = pitch

    def set_pixel(self, x, y):
        self.ds["x"] = x
        self.ds["y"] = y
        self.r.run("set_pixel")

    def set_color(self, col):
        self.ds["color"] = col



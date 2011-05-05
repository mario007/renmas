import winlib
import renmas.gui 
from tdasm import Tdasm, Runtime
import platform


bits = platform.architecture()[0]
if bits == "64bit":
    ASM = """
    #DATA
    float color[4] = 0.00, 0.00, 0.99, 0.9999 ; RGBA - fromat
    uint32 n = 50
    uint32 x = 0 
    uint32 y = 0 

    #CODE
    mov eax, dword [x]
    mov ebx, dword [y]
    mov ecx, 50
    push rax
    push rbx
    push rcx
    movaps xmm0, oword [color]
    _loop:
    mov eax, dword [esp + 16]
    mov ebx, dword [esp + 8]
    call set_pixel
    add dword [esp + 16], 1
    sub dword [esp], 1
    jnz _loop
    add esp, 24 
    #END
    """
else:
    ASM = """
    #DATA
    float color[4] = 0.00, 0.00, 0.99, 0.9999 ; RGBA - fromat
    uint32 n = 50
    uint32 x = 0 
    uint32 y = 0 

    #CODE
    mov eax, dword [x]
    mov ebx, dword [y]
    mov ecx, 50
    push eax
    push ebx
    push ecx
    movaps xmm0, oword [color]
    _loop:
    mov eax, dword [esp + 8]
    mov ebx, dword [esp + 4]
    call set_pixel
    add dword [esp + 8], 1
    sub dword [esp], 1
    jnz _loop
    add esp, 12
    #END
    """

def create_float_image(runtime):
    img = renmas.gui.ImageFloatRGBA(150, 150)
    
    img.set_pixel_asm(runtime, "set_pixel")

    asm = Tdasm()
    mc = asm.assemble(ASM)
    runtime.load("write", mc)
    runtime.run("write")
    return img
    
def blt_float_img_to_window(x, y, blitter, img, win):
    da, dpitch = win.get_addr()
    dw, dh = win.get_size()
    sa, spitch = img.get_addr()
    sw, sh = img.get_size()
    blitter.blt_floatTorgba(da, x, y, dw, dh, dpitch, sa, 0, 0, sw, sh, spitch)

win = renmas.gui.MainWindow(500, 500, "Test")

blitter = renmas.gui.Blitter()
runtime = Runtime()

img_float = create_float_image(runtime)
blt_float_img_to_window(100, 50, blitter, img_float, win)

win.redraw()
winlib.MainLoop()

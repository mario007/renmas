import platform
from math import log, exp

from tdasm import Runtime

from renmas3.core import Factory
from renmas3.macros import MacroCall

class ImageProps:
    def __init__(self, image, red_avg=None, green_avg=None, blue_avg=None,\
            lum_avg=None, lum_min=None, lum_max=None):
        self.red_avg = red_avg
        self.green_avg = green_avg
        self.blue_avg = blue_avg
        self.lum_avg = lum_avg
        self.lum_min = lum_min
        self.lum_max = lum_max
        self.image = image

def calc_img_props_py(image):
    lum_avg = red_avg = green_avg = blue_avg = 0.0
    epsilon = 0.0001
    
    lum_max = -99999.0
    lum_min = 99999.0
    width, height = image.size()

    for j in range(height):
        for i in range(width):
            r, g, b, a = image.get_pixel(i, j)
            lw = 0.2126 * r + 0.7152 * g + 0.0722 * b
            if lw > lum_max: lum_max = lw
            if lw < lum_min: lum_min = lw

            lum_avg += log(lw+epsilon)
            red_avg += log(r + epsilon)
            green_avg += log(g + epsilon)
            blue_avg += log(b + epsilon)

    npixels = float(width * height)

    lum_avg = exp(lum_avg / npixels)
    red_avg = exp(red_avg / npixels)
    green_avg = exp(green_avg / npixels)
    blue_avg = exp(blue_avg / npixels)

    img_props = ImageProps(image, red_avg=red_avg, green_avg=green_avg, blue_avg=blue_avg,\
            lum_avg=lum_avg, lum_min=lum_min, lum_max=lum_max)

    return img_props

def _calc_img_props_asm():
    bits = platform.architecture()[0]

    code = """
    #DATA
    """
    if bits == "64bit":
        code += "uint64 ptr_image, tmp_address \n" 
    else:
        code += "uint32 ptr_image, tmp_address \n" 

    code += """
    uint32 x, y, width, height, pitch 

    float luminance_min, luminance_max
    float averages[4]
    float lum[4] = 0.2126, 0.7152, 0.0722, 0.0
    uint32 mask[4] = 0x00, 0x00, 0x00, 0xFFFFFFFF
    uint32 mask2[4] = 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0x00
    float zero[4] = 0.0, 0.0, 0.0, 0.0
    float huge = 999999.0
    float small = -99999.0
    float epsilon[4]= 0.0001, 0.0001, 0.0001, 0.0001
    uint32 tmp_width, tmp_height
    uint32 x_offset
    float npixels[4]

    #CODE
    mov eax, 16 
    mov ebx, dword [x]
    imul ebx, eax
    mov dword [x_offset], ebx

    macro eq128 averages = zero {xmm7}
    macro eq32 luminance_min = huge {xmm7}
    macro eq32 luminance_max = small {xmm7}
    mov eax, dword [height]
    mov dword [tmp_height], eax

    _loop_image:
    call _calc_one_row
    sub dword [tmp_height], 1
    jnz _loop_image

    macro eq128 xmm0 = averages / npixels
    macro call fast_exp_ps
    macro eq128 averages = xmm0 {xmm7}
    
    #END

    _calc_one_row:
    mov edx, dword [width]
    mov dword [tmp_width], edx
    mov eax, dword [y]
    add eax, dword [tmp_height]
    sub eax, 1
    imul eax, dword [pitch]
    add eax, dword [x_offset]
    """
    if bits == "64bit":
        code += """
        add rax, qword [ptr_image]
        mov qword [tmp_address], rax
        _loop_pixels:
        mov rax, qword [tmp_address]
        """
    else:
        code += """
        add eax, dword [ptr_image]
        mov dword [tmp_address], eax
        _loop_pixels:
        mov eax, dword [tmp_address]
        """
    
    code += """
    macro eq128 xmm0 = eax
    macro dot xmm1 = xmm0 * lum {xmm6, xmm7}
    macro eq32 xmm2 = luminance_min
    macro call minss xmm2, xmm1
    macro eq32 xmm3 = luminance_max
    macro call maxss xmm3, xmm1

    macro eq32 luminance_min = xmm2 {xmm7}
    macro eq32 luminance_max = xmm3 {xmm7}
    macro broadcast xmm1 = xmm1[0]
    macro eq128 xmm2 = mask
    macro call andps xmm1, xmm2
    macro eq128 xmm3 = mask2
    macro call andps xmm0, xmm3
    macro call orps xmm0, xmm1
    macro eq128 xmm0 = xmm0 + epsilon
    macro call fast_log_ps
    macro eq128 averages = averages + xmm0 {xmm7}
    """ 
    if bits == "64bit":
        code += "add qword [tmp_address], 16 \n"
    else:
        code += "add dword [tmp_address], 16 \n"
    code += """
    sub dword [tmp_width], 1
    jnz _loop_pixels

    ret
    """
    assembler = Factory().create_assembler()
    runtime = Runtime()
    macro_call = MacroCall()
    macro_call.set_runtimes([runtime])
    assembler.register_macro('call', macro_call.macro_call)
    mc = assembler.assemble(code)
    #mc.print_machine_code()
    ds = runtime.load("calc_props", mc)
    return runtime, ds 

_runtime, _ds = _calc_img_props_asm()

def calc_img_props(image):
    ds = _ds
    width, height = image.size()
    ds['x'] = 0
    ds['y'] = 0
    ds['width'] = width
    ds['height'] = height

    address, pitch = image.address_info()

    ds['pitch'] = pitch  
    ds['ptr_image'] = address  
    n = float(width * height)
    ds['npixels'] = (n, n, n, n)
    _runtime.run("calc_props")

    lum_min = ds['luminance_min']
    lum_max = ds['luminance_max']
    red_avg, green_avg, blue_avg, lum_avg = ds['averages']

    img_props = ImageProps(image, red_avg=red_avg, green_avg=green_avg, blue_avg=blue_avg,\
            lum_avg=lum_avg, lum_min=lum_min, lum_max=lum_max)
    return img_props


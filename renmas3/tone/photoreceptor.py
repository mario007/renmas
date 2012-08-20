
import platform
import math
import time
from tdasm import Runtime

from .tone_map import ToneMapping
from .props import ImageProps, calc_img_props, calc_img_props_py

import renmas3.switch as proc
from renmas3.core import ImageBGRA, ImageFloatRGBA
from renmas3.macros import MacroCall, create_assembler

class PhotoreceptorOperator(ToneMapping):
    def __init__(self, m=0.6, c=0.5, a=0.5, f=1.0):

        self._asm = create_assembler()
        self._runtime = Runtime()
        self._macro_call = macro_call = MacroCall()
        self._asm.register_macro('call', macro_call.macro_call)
        macro_call.set_runtimes([self._runtime])

        self._photoreceptor_asm()

        self._m = m # contrast range usually 0.2-0.9 - you can limit this 0.0-1.0
        self._c = c # adaptation range 0.0-1.0
        self._a = a # colornes-contrast range 0.0-1.0
        self._f = f # lightnes 

    def _set_m(self, value):
        t = float(value) 
        if t > 0.0 and t < 1.0:
            self._m = t

    def _get_m(self):
        return self._m
    m = property(_get_m, _set_m)

    def _set_c(self, value):
        t = float(value) 
        if t > 0.0 and t < 1.0:
            self._c = t

    def _get_c(self):
        return self._c
    c = property(_get_c, _set_c)

    def _set_a(self, value):
        t = float(value) 
        if t > 0.0 and t < 1.0:
            self._a = t

    def _get_a(self):
        return self._a
    a = property(_get_a, _set_a)

    def _set_f(self, value):
        t = float(value) 
        if t > 0.0 and t < 100.0:
            self._f = t

    def _get_f(self):
        return self._f
    f = property(_get_f, _set_f)

    def tone_map(self, hdr_image, ldr_image):
        assert isinstance(hdr_image, ImageFloatRGBA)
        assert isinstance(ldr_image, ImageBGRA)
        #self.tone_map_py(hdr_image, ldr_image)
        self.tone_map_asm(hdr_image, ldr_image)

    def tone_map_py(self, hdr_image, ldr_image):
        m = self._m
        c = self._c
        a = self._a
        f = self._f
        
        width, height = hdr_image.size()

        props = calc_img_props_py(hdr_image)

        for j in range(height):
            for i in range(width):
                r, g, b, a1 = hdr_image.get_pixel(i, j)
                lw = 0.2126 * r + 0.7152 * g + 0.0722 * b

                ilocal_r = c * r + (1.0-c)*lw
                iglobal_r = c * props.red_avg + (1.0-c) * props.lum_avg
                ired = a * ilocal_r + (1-a) * iglobal_r

                ilocal_g = c * g + (1.0-c)*lw
                iglobal_g = c * props.green_avg + (1.0-c) * props.lum_avg
                igreen = a * ilocal_g + (1-a) * iglobal_g

                ilocal_b = c * b + (1.0-c)*lw
                iglobal_b = c * props.blue_avg + (1.0-c) * props.lum_avg
                iblue = a * ilocal_b + (1-a) * iglobal_b
                
                sigma_r = math.pow(f*ired,m)
                sigma_g = math.pow(f*igreen,m)
                sigma_b = math.pow(f*iblue,m)
                
                rd = r / (r + sigma_r)
                gd = g / (g + sigma_g)
                bd = b / (b + sigma_b)
                if rd > 0.99: rd = 0.99    
                if gd > 0.99: gd = 0.99
                if bd > 0.99: bd = 0.99
                rd = int(rd*255)
                gd = int(gd*255)
                bd = int(bd*255)

                ldr_image.set_pixel(i, j, rd, gd, bd)

    def tone_map_asm(self, hdr_image, ldr_image):
        ds = self._photo_ds

        ds['x'] = 0
        ds['y'] = 0
        width, height = hdr_image.size()
        ds['width'] = width
        ds['height'] = height

        address, pitch = hdr_image.address_info()
        ds['pitch'] = pitch  
        ds['ptr_image'] = address  
        
        props = calc_img_props(hdr_image)

        av = props.lum_avg
        ds['luminance_av'] = (av, av, av, av)
        m = self._m
        ds['m'] = (m, m, m, m)
        c = self._c
        ds['c'] = (c, c, c, c)
        a = self._a
        ds['a'] = (a, a, a, a)
        f = self._f
        ds['f'] = (f, f, f, f)

        ds['rgb_av'] = (props.red_avg, props.green_avg, props.blue_avg, 0.0)

        address, pitch = ldr_image.address_info()
        ds['ptr_output'] = address
        ds['pitch_output'] = pitch 
        self._runtime.run("photo")

    def _to_bgra_asm_code(self):
        if proc.AVX:
            to_bgra = """
                vpshufb xmm0, xmm0, xmm2
            """
        else:
            if proc.SSSE3:
                to_bgra = """
                    pshufb xmm0, xmm2 
                """
            else:
                to_bgra = """
                movaps oword [temp], xmm0
                xor eax, eax
                xor ebx, ebx
                xor edx, edx
                xor ebp, ebp
                mov eax, dword [temp + 8] ; b
                mov ebx, dword [temp + 4] ; g
                mov edx, dword [temp]     ; r
                mov ebp, dword [temp + 12]; a
                rcl ebx, 8
                rcl edx, 16
                rcl ebp, 24
                or eax, ebx
                or edx, ebp
                or eax, edx
                movd xmm0, eax

                """
        return to_bgra

    def _photoreceptor_asm(self):
        bits = platform.architecture()[0]

        code = """
            #DATA
        """
        if bits == '64bit':
            code += "uint64 ptr_image, ptr_output, tmp_address, out_address\n"
        else:
            code += "uint32 ptr_image, ptr_output, tmp_address, out_address\n"

        code += """
            uint32 x, y, width, height, pitch, pitch_output
            float luminance_av[4]
            float rgb_av[4]
            float m[4]
            float c[4]
            float a[4]
            float f[4]
            float one_minus_a[4]
            float one_minus_c[4]
            float lum[4] = 0.2126, 0.7152, 0.0722, 0.0
            float epsilon[4]= 0.0001, 0.0001, 0.0001, 0.0001
            uint32 tmp_width, tmp_height
            float one[4] = 1.0, 1.0, 1.0, 1.0
            float clamp[4] = 0.99, 0.99, 0.99, 0.99
            float scale[4] = 255.9, 255.9, 255.9, 255.9
            uint8 mask[16] = 8, 4, 0, 12, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80
            uint32 mask2[4] = 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0x00
            float lumm_one[4] = 0.0, 0.0, 0.0, 0.99
            float temp[4]
            float global_rgb_av[4]
            uint32 x1_offset, x2_offset

            #CODE
            mov eax, 16 
            mov ebx, dword [x]
            mov ecx, ebx
            imul ebx, eax
            mov dword [x1_offset], ebx
            mov eax, 4
            imul ecx, eax
            mov dword [x2_offset], ecx 


            macro eq128 one_minus_c = one - c {xmm7} 
            macro eq128 one_minus_a = one - a {xmm7}
            macro eq128 xmm0 = c * rgb_av
            macro eq128 xmm1 = one_minus_c * luminance_av
            macro eq128 xmm2 = xmm0 + xmm1
            macro eq128 global_rgb_av = xmm2 * one_minus_a {xmm7}

            mov eax, dword [height]
            mov dword [tmp_height], eax
            _loop_image:
            call _calc_one_row
            sub dword [tmp_height], 1
            jnz _loop_image
            #END

            _calc_one_row:
            mov edx, dword [width]
            mov dword [tmp_width], edx
            mov eax, dword [y]
            add eax, dword [tmp_height]
            sub eax, 1
            mov ecx, eax
            imul eax, dword [pitch]
            add eax, dword [x1_offset]
        """
        if bits == '64bit':
            code += """
            add rax, qword [ptr_image]
            mov qword [tmp_address], rax

            imul ecx, dword [pitch_output]
            add ecx, dword[x2_offset]
            add rcx, qword [ptr_output]
            mov qword [out_address], rcx

            _loop_pixels:
            mov rax, qword [tmp_address]
            """
        else:
            code += """
            add eax, dword [ptr_image]
            mov dword [tmp_address], eax

            imul ecx, dword [pitch_output]
            add ecx, dword[x2_offset]
            add ecx, dword [ptr_output]
            mov dword [out_address], ecx

            _loop_pixels:
            mov eax, dword [tmp_address]
            """

        code += """

            macro eq128 xmm0 = eax
            macro dot xmm1 = xmm0 * lum {xmm6, xmm7}
            macro broadcast xmm1 = xmm1[0]
            macro eq128 xmm2 = xmm0 * c
            macro eq128 xmm3 = xmm1 * one_minus_c + xmm2
            macro eq128 xmm4 = xmm3 * a + global_rgb_av
            macro eq128 temp = xmm0 {xmm7}
            macro eq128 xmm0 = xmm4 * f
            macro eq128 xmm1 = m
            macro call fast_pow_ps
            macro eq128 xmm1 = temp
            macro eq128 xmm2 = xmm0
            macro eq128 xmm0 = xmm1
            macro eq128 xmm1 = xmm1 + xmm2
            macro eq128 xmm0 = xmm0 / xmm1


            ; clamp value to 0.0-0.99 and put 0.99 in alpha channel
            macro eq128 xmm5 = mask2
            macro call andps xmm0, xmm5
            macro eq128 xmm0 = xmm0 + lumm_one

            macro eq128 xmm6 = clamp
            macro call zero xmm5
            macro call maxps xmm0, xmm5
            macro call minps xmm0, xmm6
            macro eq128 xmm0 = xmm0 * scale

            macro eq128 xmm2 = mask
            macro call float_to_int xmm0, xmm0
        """
        code += self._to_bgra_asm_code() + """
            ;pshufb xmm0, xmm2 
        """
        if bits == '64bit':
            code += """
            mov rax, qword [out_address] 
            macro eq32 eax = xmm0 {xmm7}

            add qword [tmp_address], 16
            add qword [out_address], 4 
            """
        else:
            code += """
            mov eax, dword [out_address] 
            macro eq32 eax = xmm0 {xmm7}

            add dword [tmp_address], 16
            add dword [out_address], 4 
            """
        code += """
            sub dword [tmp_width], 1
            jnz _loop_pixels

            ret
        """
        mc = self._asm.assemble(code)
        #mc.print_machine_code()
        self._photo_ds = self._runtime.load("photo", mc)


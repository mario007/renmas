
import platform
import math
import time
from tdasm import Runtime

from .tone_map import ToneMapping
from .props import ImageProps, calc_img_props, calc_img_props_py

import renmas3.switch as proc
from renmas3.core import Factory, ImageBGRA, ImageFloatRGBA
from renmas3.macros import MacroCall

class ReinhardOperator(ToneMapping):
    def __init__(self, scene_key=0.18, saturation=0.6):
        self._asm = Factory().create_assembler()
        self._runtime = Runtime()
        self._macro_call = macro_call = MacroCall()
        self._asm.register_macro('call', macro_call.macro_call)
        macro_call.set_runtimes([self._runtime])

        self._reinhard_asm()

        self._key = float(scene_key)
        self._saturation = float(saturation)

    def _set_key(self, value):
        self._key = float(value) 

    def _get_key(self):
        return self._key
    scene_key = property(_get_key, _set_key)

    def _set_saturation(self, value):
        self._saturation = float(value) 

    def _get_saturation(self):
        return self._saturation
    saturation = property(_get_saturation, _set_saturation)

    def tone_map(self, hdr_image, ldr_image):
        assert isinstance(hdr_image, ImageFloatRGBA)
        assert isinstance(ldr_image, ImageBGRA)
        #self.tone_map_py(hdr_image, ldr_image)
        self.tone_map_asm(hdr_image, ldr_image)

    def tone_map_py(self, hdr_image, ldr_image):
        # user parameters
        scene_key = self._key # user parameter may be estimated as initial value
        s = self._saturation 

        props = calc_img_props_py(hdr_image)

        epsilon = 0.0001
        lwhite2 = props.lum_max * props.lum_max + 0.0001 
        lum_avg = props.lum_avg + 0.0001
        width, height = hdr_image.size()

        for j in range(height):
            for i in range(width):
                r, g, b, a = hdr_image.get_pixel(i, j)
                lw = 0.2126 * r + 0.7152 * g + 0.0722 * b + epsilon
                lm = (scene_key*lw) / lum_avg 
                #ld = lm / (1.0 + lm)
                lw2 = 1.0 + lm / lwhite2 
                ld = lm * lw2 / (1.0 + lm)
                rd = ld * math.pow((r+epsilon)/lw,s)
                gd = ld * math.pow((g+epsilon)/lw,s)
                bd = ld * math.pow((b+epsilon)/lw,s)
                if rd > 0.99: rd = 0.99    
                if gd > 0.99: gd = 0.99
                if bd > 0.99: bd = 0.99
                rd = int(rd*255)
                gd = int(gd*255)
                bd = int(bd*255)

                ldr_image.set_pixel(i, j, rd, gd, bd)

    def tone_map_asm(self, hdr_image, ldr_image):

        ds = self._reinhard_ds
        ds['x'] = 0
        ds['y'] = 0
        width, height = hdr_image.size()
        ds['width'] = width
        ds['height'] = height

        address, pitch = hdr_image.address_info()

        ds['pitch'] = pitch  
        ds['ptr_image'] = address  
        ds['scene_key'] = self._key 
        
        img_props = calc_img_props(hdr_image)
        lwhite2 = img_props.lum_max * img_props.lum_max + 0.0001 

        ds['lwhite2'] = lwhite2 
        ds['luminance_av'] = img_props.lum_avg + 0.0001
        s = self._saturation
        ds['semi_saturation'] = (s, s, s, s)
        address, pitch = ldr_image.address_info()
        ds['ptr_output'] = address
        ds['pitch_output'] = pitch 

        self._runtime.run("reinhard")

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

    def _reinhard_asm(self):
        bits = platform.architecture()[0]

        code = """
            #DATA
            """
        if bits == '64bit':
            code += "uint64 ptr_image, ptr_output, tmp_address, out_address \n"
        else:
            code += "uint32 ptr_image, ptr_output, tmp_address, out_address \n"

        code += """
            uint32 x, y, width, height 
            uint32 pitch, pitch_output
            float luminance_min, luminance_max
            float lwhite2
            float luminance_av
            float lum[4] = 0.2126, 0.7152, 0.0722, 0.0
            float epsilon[4]= 0.0001, 0.0001, 0.0001, 0.0001
            uint32 tmp_width, tmp_height
            float semi_saturation[4]
            float scene_key
            float one = 1.0
            float tmp_Ld
            float clamp[4] = 0.99, 0.99, 0.99, 0.99
            float scale[4] = 255.9, 255.9, 255.9, 255.9
            uint8 mask[16] = 8, 4, 0, 12, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80
            uint32 mask2[4] = 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0x00
            float lumm_one[4] = 0.0, 0.0, 0.0, 0.99
            float temp[4]
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
            macro eq32 xmm1 = xmm1 + epsilon
            macro eq32 xmm2 = xmm1 * scene_key / luminance_av
            macro eq32 xmm3 = xmm2 / lwhite2 + one
            macro eq32 xmm4 = xmm2 + one
            macro eq32 xmm5 = xmm2 * xmm3 / xmm4

            macro eq32 tmp_Ld = xmm5 {xmm7}
            macro eq128 xmm0 = xmm0 + epsilon
            macro broadcast xmm1 = xmm1[0]
            macro eq128 xmm0 = xmm0 / xmm1

            macro eq128 xmm1 = semi_saturation
            macro call fast_pow_ps
            macro eq32 xmm1 = tmp_Ld
            macro broadcast xmm1 = xmm1[0]
            macro eq128 xmm0 = xmm0 * xmm1

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
        self._reinhard_ds = self._runtime.load("reinhard", mc)


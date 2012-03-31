
import math
import time
from tdasm import Runtime

from .tone_map import ToneMapping, ImageProps
from ..macros import MacroCall
import renmas2
import renmas2.switch as proc

class ReinhardOperator(ToneMapping):
    def __init__(self, scene_key=None, saturation=None):
        self.factory = renmas2.core.Factory()
        self.asm = self.factory.create_assembler()
        self.runtime = Runtime()
        self._macro_call = macro_call = MacroCall()
        self.asm.register_macro('call', macro_call.macro_call)
        macro_call.set_runtimes([self.runtime])

        self._calc_average_asm()
        self._photographic_asm()

        self._key = 0.18 #lighnes
        self._saturation = 0.6

        self.scene_key = scene_key
        self.saturation = saturation

    def _set_key(self, value):
        try:
            t = float(value) 
            if t > 0.0 and t < 100.0:
                self._key = t
        except:
            pass #TODO log -- or some other notification

    def _get_key(self):
        return self._key
    scene_key = property(_get_key, _set_key)

    def _set_saturation(self, value):
        try:
            t = float(value) 
            if t > 0.0 and t < 1.0:
                self._saturation = t
        except:
            pass #TODO log -- or some other notification

    def _get_saturation(self):
        return self._saturation
    saturation = property(_get_saturation, _set_saturation)

    #in_picture - RGBA float picture
    #out_picture - RGBA int picture
    def tone_map(self, ldr_picture, hdr_picture, x, y, width, height):

        #start = time.clock()
        img_props = self._calc_average_fast(hdr_picture, x, y, width, height)
        #img_props = self._calc_average(hdr_picture, x, y, width, height)

        self._photographic_fast(ldr_picture, hdr_picture, x, y, width, height, img_props)
        #self._photographic(ldr_picture, hdr_picture, x, y, width, height, img_props)
        #print("Photographic time:", time.clock()-start)
        

    def _photographic_fast(self, ldr_picture, hdr_picture, x, y, width, height, img_props):
        self._photographic_ds['x'] = x
        self._photographic_ds['y'] = y
        self._photographic_ds['width'] = width
        self._photographic_ds['height'] = height
        address, pitch = hdr_picture.get_addr()
        self._photographic_ds['pitch'] = pitch  
        self._photographic_ds['ptr_image'] = address  
        
        self._photographic_ds['scene_key'] = self._key 
        lwhite2 = img_props.luminance_max * img_props.luminance_max + 0.0001 
        self._photographic_ds['lwhite2'] = lwhite2 
        self._photographic_ds['luminance_av'] = img_props.luminance_av + 0.0001
        s = self._saturation
        self._photographic_ds['semi_saturation'] = (s, s, s, s)
        address, pitch = ldr_picture.get_addr()
        self._photographic_ds['ptr_output'] = address
        self._photographic_ds['pitch_output'] = pitch 
        self.runtime.run("photographic")


    def _photographic(self, ldr_picture, hdr_picture, x, y, width, height, img_props):
        scene_key = self._key # user parameter may be estimated as initial value
        s = self._saturation 
        epsilon = 0.0001
        lwhite2 = img_props.luminance_max * img_props.luminance_max + 0.0001 
        luminance_av = img_props.luminance_av + 0.0001
        for j in range(y, y + height):
            for i in range(x, x + width):
                r, g, b, a = hdr_picture.get_pixel(i, j)
                lw = 0.2126 * r + 0.7152 * g + 0.0722 * b + epsilon
                lm = (scene_key*lw) / luminance_av 
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

                ldr_picture.set_pixel(i, j, rd, gd, bd)

    def _photographic_asm(self):
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


        code = """
            #DATA
            uint32 ptr_image, pitch
            uint32 x, y, width, height 
            uint32 ptr_output, pitch_output
            float luminance_min, luminance_max
            float lwhite2
            float luminance_av
            float lum[4] = 0.2126, 0.7152, 0.0722, 0.0
            float epsilon[4]= 0.0001, 0.0001, 0.0001, 0.0001
            uint32 tmp_width, tmp_height, tmp_address, out_address
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
            add eax, dword [ptr_image]
            mov dword [tmp_address], eax

            imul ecx, dword [pitch_output]
            add ecx, dword[x2_offset]
            add ecx, dword [ptr_output]
            mov dword [out_address], ecx
            

            _loop_pixels:
            mov eax, dword [tmp_address]
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
        code += to_bgra + """
            ;pshufb xmm0, xmm2 

            mov eax, dword [out_address] 
            macro eq32 eax = xmm0 {xmm7}

            add dword [tmp_address], 16
            add dword [out_address], 4 
            sub dword [tmp_width], 1
            jnz _loop_pixels

            ret
        """
        mc = self.asm.assemble(code)
        #mc.print_machine_code()
        self._photographic_ds = self.runtime.load("photographic", mc)

    def _calc_average_asm(self):
        code = """
            #DATA
            uint32 ptr_image, pitch
            uint32 x, y, width, height 

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
            uint32 tmp_address
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
            add eax, dword [ptr_image]
            mov dword [tmp_address], eax

            _loop_pixels:
            mov eax, dword [tmp_address]
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
            
            add dword [tmp_address], 16
            sub dword [tmp_width], 1
            jnz _loop_pixels

            ret
        """
        mc = self.asm.assemble(code)
        #mc.print_machine_code()
        self._average_ds = self.runtime.load("calc_averages", mc)

    def _calc_average_fast(self, hdr_picture, x, y, width, height):
        self._average_ds['x'] = x
        self._average_ds['y'] = y
        self._average_ds['width'] = width
        self._average_ds['height'] = height
        address, pitch = hdr_picture.get_addr()
        self._average_ds['pitch'] = pitch  
        self._average_ds['ptr_image'] = address  
        n = float(width * height)
        self._average_ds['npixels'] = (n, n, n, n)
        self.runtime.run("calc_averages")

        lmin = self._average_ds['luminance_min']
        lmax = self._average_ds['luminance_max']
        red_av, green_av, blue_av, luminance_av = self._average_ds['averages']
        img_props = ImageProps(red_av, green_av, blue_av, luminance_av, lmin, lmax)
        return img_props

    def _calc_average(self, hdr_picture, x, y, width, height):

        luminance_av = 0.0
        red_av = green_av = blue_av = 0.0
        epsilon = 0.0001
        
        lmax = -99999.0
        lmin = 99999.0
        for j in range(y, y + height):
            for i in range(x, x + width):
                r, g, b, a = hdr_picture.get_pixel(i, j)
                lw = 0.2126 * r + 0.7152 * g + 0.0722 * b
                if lw > lmax: lmax = lw
                if lw < lmin: lmin = lw
                luminance_av += math.log(lw+epsilon)
                red_av += math.log(r + epsilon)
                green_av += math.log(g + epsilon)
                blue_av += math.log(b + epsilon)


        luminance_av = luminance_av / (float(width*height))
        luminance_av = math.exp(luminance_av)
        red_av = red_av / (float(width*height))
        red_av = math.exp(red_av)
        green_av = green_av / (float(width*height))
        green_av = math.exp(green_av)
        blue_av = blue_av / (float(width*height))
        blue_av = math.exp(blue_av)

        img_props = ImageProps(red_av, green_av, blue_av, luminance_av, lmin, lmax)
        return img_props

    def _show_props(self, img_props):
        print ("Luminance min:", img_props.luminance_min)
        print ("Luminance max:", img_props.luminance_max)
        print ("Luminance average ", img_props.luminance_av)
        print ("Red average ", img_props.red_av)
        print ("Green average ", img_props.green_av)
        print ("Blue average ", img_props.blue_av)


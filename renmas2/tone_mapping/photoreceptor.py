
import math
import time
from tdasm import Runtime

from .tone_map import ToneMapping, ImageProps
from ..macros import MacroCall
import renmas2
import renmas2.switch as proc

class PhotoreceptorOperator(ToneMapping):
    def __init__(self, m=None, c=None, a=None, f=None):
        self.factory = renmas2.core.Factory()
        self.asm = self.factory.create_assembler()
        self.runtime = Runtime()
        self._macro_call = macro_call = MacroCall()
        self.asm.register_macro('call', macro_call.macro_call)
        macro_call.set_runtimes([self.runtime])

        self._calc_average_asm()
        self._sigmond_asm()

        self._m = 0.6 # contrast range usually 0.2-0.9 - you can limit this 0.0-1.0
        self._c = 0.5 # adaptation range 0.0-1.0
        self._a = 0.5 # colornes-contrast range 0.0-1.0
        self._f = 1.0 # lightnes 
        self.f = f
        self.m = m
        self.c = c
        self.a = a

    def _set_m(self, value):
        try:
            t = float(value) 
            if t > 0.0 and t < 1.0:
                self._m = t
        except:
            pass #TODO log -- or some other notification

    def _get_m(self):
        return self._m
    m = property(_get_m, _set_m)

    def _set_c(self, value):
        try:
            t = float(value) 
            if t > 0.0 and t < 1.0:
                self._c = t
        except:
            pass #TODO log -- or some other notification

    def _get_c(self):
        return self._c
    c = property(_get_c, _set_c)

    def _set_a(self, value):
        try:
            t = float(value) 
            if t > 0.0 and t < 1.0:
                self._a = t
        except:
            pass #TODO log -- or some other notification

    def _get_a(self):
        return self._a
    a = property(_get_a, _set_a)

    def _set_f(self, value):
        try:
            t = float(value) 
            if t > 0.0 and t < 100.0:
                self._f = t
        except:
            pass #TODO log -- or some other notification

    def _get_f(self):
        return self._f
    f = property(_get_f, _set_f)

    #in_picture - RGBA float picture
    #out_picture - RGBA int picture
    def tone_map(self, ldr_picture, hdr_picture, x, y, width, height):

        #start = time.clock()
        img_props = self._calc_average_fast(hdr_picture, x, y, width, height)
        #img_props = self._calc_average(hdr_picture, x, y, width, height)

        self._sigmond_fast(ldr_picture, hdr_picture, x, y, width, height, img_props)
        #self._sigmond(ldr_picture, hdr_picture, x, y, width, height, img_props)

        #print("Photographic time:", time.clock()-start)
        

    def _sigmond(self, ldr_picture, hdr_picture, x, y, width, height, img_props):
        m = self._m
        c = self._c
        a = self._a
        f = self._f

        for j in range(y, y + height):
            for i in range(x, x + width):
                r, g, b, a1 = hdr_picture.get_pixel(i, j)
                lw = 0.2126 * r + 0.7152 * g + 0.0722 * b
                ilocal_r = c * r + (1.0-c)*lw
                iglobal_r = c * img_props.red_av + (1.0-c) * img_props.luminance_av
                ired = a * ilocal_r + (1-a) * iglobal_r

                ilocal_g = c * g + (1.0-c)*lw
                iglobal_g = c * img_props.green_av + (1.0-c) * img_props.luminance_av
                igreen = a * ilocal_g + (1-a) * iglobal_g

                ilocal_b = c * b + (1.0-c)*lw
                iglobal_b = c * img_props.blue_av + (1.0-c) * img_props.luminance_av
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

                ldr_picture.set_pixel(i, j, rd, gd, bd)

    def _sigmond_fast(self, ldr_picture, hdr_picture, x, y, width, height, img_props):
        self._sigmond_ds['x'] = x
        self._sigmond_ds['y'] = y
        self._sigmond_ds['width'] = width
        self._sigmond_ds['height'] = height
        address, pitch = hdr_picture.get_addr()
        self._sigmond_ds['pitch'] = pitch  
        self._sigmond_ds['ptr_image'] = address  
        
        av = img_props.luminance_av
        self._sigmond_ds['luminance_av'] = (av, av, av, av)
        m = self._m
        self._sigmond_ds['m'] = (m, m, m, m)
        c = self._c
        self._sigmond_ds['c'] = (c, c, c, c)
        a = self._a
        self._sigmond_ds['a'] = (a, a, a, a)
        f = self._f
        self._sigmond_ds['f'] = (f, f, f, f)
        ip = img_props
        self._sigmond_ds['rgb_av'] = (ip.red_av, ip.green_av, ip.blue_av, 0.0)

        address, pitch = ldr_picture.get_addr()
        self._sigmond_ds['ptr_output'] = address
        self._sigmond_ds['pitch_output'] = pitch 
        self.runtime.run("sigmond")


    def _sigmond_asm(self):
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
            uint32 tmp_width, tmp_height, tmp_address, out_address
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
        self._sigmond_ds = self.runtime.load("sigmond", mc)


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


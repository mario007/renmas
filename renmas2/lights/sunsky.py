
from random import random
import math
from math import sin, asin, pi, radians, cos, atan2, exp, tan, acos, atan2

from ..core import Vector3, Spectrum
from .light import EnvironmentLight
import renmas2.switch as proc

# latitude - (0 - 360)
# longitude - (-90, 90) south to north
# sm = standard meridian -- actually time zone number 
# jd = julian day (1 - 365)
# time_of_day (0.0 - 23.99) 14.25 = 2.15PM
# turbidity (1.0, 30+) 2-6 are most useful for clear day 

class SunSky(EnvironmentLight):
    def __init__(self, renderer, latitude, longitude, sm, jd, time_of_day, turbidity):
        self._ko = [(300, 10.0), (305, 4.8), (310, 2.7), (315, 1.35), (320, 0.8), 
        (325, 0.380), (330, 0.160),
        (335, 0.075), (340, 0.04), (345, 0.019), (350, 0.007), (355, 0.0), (445, 0.003), (450, 0.003),
        (455, 0.004), (460, 0.006), (465, 0.008), (470, 0.009), (475, 0.012), (480, 0.014),
        (485, 0.017), (490, 0.021), (495, 0.025), (500, 0.03), (505, 0.035),
        (510, 0.04), (515, 0.045), (520, 0.048), (525, 0.057), (530, 0.063), (535, 0.07),
        (540, 0.075), (545, 0.08), (550, 0.085), (555, 0.095), (560, 0.103), (565, 0.110),
        (570, 0.120), (575, 0.122), (580, 0.120), (585, 0.118), (590, 0.115), (595, 0.120),
        (600, 0.125), (605, 0.130), (610, 0.120), (620, 0.105), (630, 0.09), (640, 0.079),
        (650, 0.067), (660, 0.057), (670, 0.048), (680, 0.036), (690, 0.028), (700, 0.023),
        (710, 0.018), (720, 0.014), (730, 0.011), (740, 0.010), (750, 0.09), (760, 0.007),
        (770, 0.004), (780, 0.0), (790, 0.0)]

        self._kg = [(759, 0.0), (760, 3.0), (770, 0.210), (771, 0.0)]

        self._kwa = [(689, 0.0), (690, 0.0160), (700, 0.0240), (710, 0.0125), (720, 1.0), (730, 0.870),
        (740, 0.061), (750, 0.001), (760, 0.00001), (770, 0.00001), (780, 0.0006),
        (790, 0.0175), (800, 0.0360)]

        self._sol = [(380, 165.5), (390, 162.3), (400, 211.2), (410, 258.8), (420, 258.2),
        (430, 242.3), (440, 267.6), (450, 296.6), (460, 305.4), (470, 300.6),
        (480, 306.6), (490, 288.3), (500, 287.1), (510, 278.2), (520, 271.0),
        (530, 272.3), (540, 263.6), (550, 255.0), (560, 250.6), (570, 253.1),
        (580, 253.5), (590, 251.3), (600, 246.3), (610, 241.7), (620, 236.8),
        (630, 232.1), (640, 228.2), (650, 223.4), (660, 219.7), (670, 215.3),
        (680, 211.0), (690, 207.3), (700, 202.4), (710, 198.7), (720, 194.3),
        (730, 190.7), (740, 186.3), (750, 182.6)]


        self._latitude = latitude
        self._longitude = longitude
        self._sm = sm * 15.0 # sm is actually time zone number (east to west, zero based)
        self._jd = jd
        self._time_of_day = time_of_day
        self._turbidity = turbidity
        self._renderer = renderer

        self._calc_sun_position()

        #TODO -- create spectrum
        sun_radiance = self._compute_attenuated_sunlight()

        sun_solid_angle = 0.25 * pi * 1.39 * 1.39 / (150 * 150) # = 6.7443e-05

        T = self._turbidity
        self._perez_Y = [0.0 for i in range(6)]
        self._perez_Y[1] =    0.17872 *T  - 1.46303
        self._perez_Y[2] =   -0.35540 *T  + 0.42749
        self._perez_Y[3] =   -0.02266 *T  + 5.32505
        self._perez_Y[4] =    0.12064 *T  - 2.57705
        self._perez_Y[5] =   -0.06696 *T  + 0.37027
      
        self._perez_x = [0.0 for i in range(6)]
        self._perez_x[1] =   -0.01925 *T  - 0.25922
        self._perez_x[2] =   -0.06651 *T  + 0.00081
        self._perez_x[3] =   -0.00041 *T  + 0.21247
        self._perez_x[4] =   -0.06409 *T  - 0.89887
        self._perez_x[5] =   -0.00325 *T  + 0.04517
      
        self._perez_y = [0.0 for i in range(6)]
        self._perez_y[1] =   -0.01669 *T  - 0.26078
        self._perez_y[2] =   -0.09495 *T  + 0.00921
        self._perez_y[3] =   -0.00792 *T  + 0.21023
        self._perez_y[4] =   -0.04405 *T  - 1.65369
        self._perez_y[5] =   -0.01092 *T  + 0.05291

        chi = (4.0/9.0 - T / 120.0) * (pi - 2 * self._theta_sun)
        self._zenith_Y = (4.0453 * T - 4.9710) * tan(chi) - 0.2155 * T + 2.4192
        self._zenith_Y *= 1000  # conversion from kcd/m^2 to cd/m^2

        T2 = T * T
        theta = self._theta_sun
        theta2 = self._theta_sun * self._theta_sun
        theta3 = self._theta_sun * self._theta_sun * self._theta_sun

        row1 = 0.00165 * theta3 - 0.00374 * theta2 + 0.00208 * theta + 0.0
        row2 = -0.02902 * theta3 + 0.06377 * theta2 - 0.03202 * theta + 0.00394
        row3 = 0.11693 * theta3 - 0.21196 * theta2 + 0.06052 * theta + 0.25885
        self._zenith_x = row1 * T2 + row2 * T + row3

        row1 = 0.00275 * theta3 - 0.00610 * theta2 + 0.00316 * theta + 0.0
        row2 = -0.04214 * theta3 + 0.08970 * theta2 - 0.04153 * theta + 0.00515
        row3 = 0.15346 * theta3 - 0.26756 * theta2 + 0.06669 * theta + 0.26688
        self._zenith_y = row1 * T2 + row2 * T + row3

    def _calc_sun_position(self):
        
        t1 = 0.170 * sin(4 * pi * (self._jd - 80) / 373.0)
        t2 = -0.129 * sin(2 * pi * (self._jd - 8) / 355.0)
        t3 = (self._sm - self._longitude) / 15.0 

        solar_time = self._time_of_day + t1 + t2 + t3 

        solar_declination = 0.4093 * sin(2 * pi * (self._jd - 81) / 368.0)

        solar_altitude = asin(sin(radians(self._latitude))* sin(solar_declination) - 
                cos(radians(self._latitude)) * cos(solar_declination) * cos(pi * solar_time / 12.0))

        self._theta_sun = theta_sun = pi / 2.0 - solar_altitude 

        opp = -cos(solar_declination) * sin(pi * solar_time / 12.0)
        adj = -cos(radians(self._latitude)) * sin(solar_declination) + sin(radians(self._latitude)) * cos(solar_declination) * cos(pi * solar_time / 12.0)

        solar_azimuth = atan2(opp, adj)

        self._phi_sun = phi_sun = -solar_azimuth

        self._dir_to_sun = Vector3(cos(phi_sun)*sin(theta_sun), sin(phi_sun)*sin(theta_sun), cos(theta_sun))


    def _compute_attenuated_sunlight(self):
        theta_sun = self._theta_sun
        turbidity = self._turbidity
        
        ko_curve = self._create_samples(self._ko, 91, 350, 800)
        kg_curve = self._create_samples(self._kg, 91, 350, 800)
        kwa_curve = self._create_samples(self._kwa, 91, 350, 800)
        sol_curve = self._create_samples(self._sol, 91, 350, 800)
        lambdas = self._lambdas(91, 350, 800)

        beta = 0.04608365822050 * turbidity - 0.04586025928522
        m = 1.0 / (cos(theta_sun) + 0.15 * pow(93.885 - theta_sun / pi * 180.0, -1.253))
        
        sun_radiance = []
        for i in range(len(lambdas)):
            lam = lambdas[i]

            # rayleigh scattering
            tau_r = exp( -m * 0.008735 * pow(lam/1000, -4.08))

            alpha = 1.3
            # lambda should be in um
            # Aerosal (water + dust) attenuation
			# beta - amount of aerosols present 
			# alpha - ratio of small to large particle sizes. (0:4,usually 1.3)
            tau_a = exp(-m * beta * pow(lam/1000, -alpha))

			# Attenuation due to ozone absorption  
			# lozone - amount of ozone in cm(NTP) 
            lozone = 0.35
            tau_o = exp(-m * ko_curve[i] * lozone)

            # Attenuation due to mixed gases absorption  
            tau_g = exp(-1.41 * kg_curve[i] * m / pow(1 + 118.93 * kg_curve[i] * m, 0.45))

            #Attenuation due to water vapor absorbtion  
            # w - precipitable water vapor in centimeters (standard = 2) 
            w = 2.0
            tau_wa = exp(-0.2385 * kwa_curve[i] * w * m / pow(1 + 20.07 * kwa_curve[i] * w * m, 0.45))
            
            # 100 comes from sol_curve in wrong units
            amplitude = 100 * sol_curve[i] * tau_r * tau_a * tau_o * tau_g * tau_wa

            sun_radiance.append((lam, amplitude))

        return sun_radiance

    #val - values at certain wavelength - tuple (lambda, value)
    # required number of samples 
    #start - start lambda
    #end - end lambda
    def _create_samples(self, vals, nsamples, start_lambda, end_lambda):
        nspec = nsamples 
        start = start_lambda
        end = end_lambda
        s = []
        for i in range(nspec):
            lambda0 = self.lerp(float(i)/float(nspec), start, end)
            lambda1 = self.lerp(float(i+1)/float(nspec), start, end)
            s.append(self._average_spectrum(vals, lambda0, lambda1))
        return s

    def _average_spectrum(self, vals, lambda1, lambda2):
        # out of bounds or single value
        lam1, val1 = vals[0]
        if lambda2 <= lam1: return val1
        lam2, val2 = vals[-1]
        if lambda1 >= lam2: return val2
        if len(vals) == 1: return val1

        # add contribution of constant segments before and after samples
        s = 0.0
        if lambda1 < lam1:
            s += val1 * (lam1 - lambda1)
        if lambda2 > lam2:
            s += val2 * (lambda2 - lam2)
        
        # advance to first relevant wavelength segment
        i = 0
        while lambda1 > vals[i+1][0]:
            i += 1

        def interp(w, i):
            return self.lerp((w-vals[i][0])/(vals[i+1][0]-vals[i][0]), vals[i][1], vals[i+1][1])

        def average(seg_start, seg_end, i):
            return 0.5 * (interp(seg_start, i) + interp(seg_end, i))

        # loop over wavelength sample segments and add contributions
        n = len(vals)
        while i+1 < n and lambda2 >= vals[i][0]:
            seg_start = max(lambda1, vals[i][0])
            seg_end = min(lambda2, vals[i+1][0])
            s += average(seg_start, seg_end, i) * (seg_end - seg_start)
            i += 1
        return s / (lambda2 - lambda1)

    # linear intepolation
    def lerp(self, t, v1, v2):
        return (1.0 - t) * v1 + t * v2

    def _lambdas(self, nsamples, start_lambda, end_lambda): #return array of lambda samples
        nspec = nsamples 
        start = start_lambda
        end = end_lambda
        s = []
        for i in range(nspec):
            lambda0 = self.lerp(float(i)/float(nspec), start, end)
            lambda1 = self.lerp(float(i+1)/float(nspec), start, end)
            s.append(lambda0)
        return s

    def get_sky_spectrum(self, direction):
        d = direction
        if d.y < 0.0: 
            return self._renderer.converter.zero_spectrum() 
        if d.y < 0.001:
            d = Vector3(d.x, 0.001, d.z)
            d.normalize()
        
        theta = acos(d.y)
        phi = atan2(d.x, d.z)
        if phi < 0.0:
            phi = phi + 2 * pi
        
        gamma = self._angle_beetween(theta, phi, self._theta_sun, self._phi_sun)

        x = self._perez_function(self._perez_x, theta, gamma, self._zenith_x)
        y = self._perez_function(self._perez_y, theta, gamma, self._zenith_y)
        Y = self._perez_function(self._perez_Y, theta, gamma, self._zenith_Y)

        if self._renderer.spectral_rendering:
            spec = self._renderer.converter.chromacity_to_spectrum(x, y)
            return spec * (Y / self._renderer.converter.Y(spec))
        else:
            x1 = x * Y / y 
            y1 = Y 
            z1 = (1.0 - x - y) * Y / y
            rgb = self._renderer.converter.xyz_to_rgb(x1, y1, z1)
            return Spectrum(False, rgb)

    # xmm0 = direction
    # eax - pointer to spectrum
    def get_sky_spectrum_asm(self, label, runtimes):

        perez = "perez" + str(abs(hash(self)))
        self._perez_function_asm(perez, runtimes, self._renderer.assembler)

        ASM = """
            #DATA
        """
        ASM += self._renderer.structures.structs(('spectrum',)) +  """
            spectrum zero_spectrum
            float con1 = 0.001
            uint32 mask[4] = 0xFFFFFFFF, 0x00000000, 0xFFFFFFFF, 0x00000000
            float con2[4] = 0.0, 0.001, 0.0, 0.0
            float HALF_PI = 1.570796323
            float HALF_PI_NEG = -1.570796323
            float one[4] = 1.0, 1.0, 1.0, 1.0
            float minus_one[4] = -1.0, -1.0, -1.0, -1.0
            float TWO_PI = 6.2831853
            float PI = 3.1415926535

            float theta, gamma, phi
            float theta_sun, phi_sun
            float direction[4]

            float perez_x[6]
            float perez_y[6]
            float perez_Y[6]
            float zenith_x, zenith_y, zenith_Y
            float x, y, Y
            float XYZ[4]
            float temp1, temp2, temp3, temp4
            uint32 ptr_spectrum
            #CODE
        """
        ASM += " global " + label + ":\n" + """
        mov dword [ptr_spectrum], eax
        macro broadcast xmm1 = xmm0[1]
        macro call zero xmm2
        macro if xmm1 > xmm2 goto _next
        mov ebx, zero_spectrum
        macro spectrum eax = ebx
        ret

        _next:
        macro if xmm1 > con1 goto _next2
        macro eq128 xmm3 = mask
        macro call andps xmm0, xmm3
        macro eq128 xmm0 = xmm0 + con2
        macro normalization xmm0 {xmm6, xmm7}

        _next2:
        macro eq128 direction = xmm0 {xmm7}
        macro broadcast xmm0 = xmm0[1]
        macro call fast_acos_ss
        macro eq32 theta = xmm0 {xmm7}

        macro eq128 xmm0 = direction
        macro broadcast xmm2 = xmm0[2]
        macro eq32 xmm1 = one / xmm2
        macro call fast_atanr2_ss
        
        macro call zero xmm1
        macro if xmm0 > xmm1 goto _next3
        macro eq32 xmm0 = xmm0 + TWO_PI

        _next3:
        macro eq32 phi = xmm0 {xmm7}
        ; cacluate angle between direction and sun
        call _angle_calc

        mov eax, perez_x 
        macro eq32 xmm0 = theta
        macro eq32 xmm1 = gamma 
        macro eq32 xmm2 = zenith_x 
        macro eq32 xmm3 = theta_sun 
        """
        ASM += "call " + perez + """

        macro eq32 x = xmm0 {xmm7}
        mov eax, perez_y 
        macro eq32 xmm0 = theta
        macro eq32 xmm1 = gamma 
        macro eq32 xmm2 = zenith_y 
        macro eq32 xmm3 = theta_sun 
        """
        ASM += "call " + perez + """

        macro eq32 y = xmm0 {xmm7}
        mov eax, perez_Y 
        macro eq32 xmm0 = theta
        macro eq32 xmm1 = gamma 
        macro eq32 xmm2 = zenith_Y 
        macro eq32 xmm3 = theta_sun 
        """
        ASM += "call " + perez + """
        macro eq32 Y = xmm0 {xmm7}
        """
        if self._renderer.spectral_rendering:
            ASM += """
            macro eq32 xmm0 = x
            macro eq32 xmm1 = y
            mov eax, dword [ptr_spectrum]
            """
            chrom_conv = "chromacity_to_spectrum" + str(abs(hash(self)))
            self._renderer.converter.chromacity_to_spectrum_asm(chrom_conv, runtimes)
            ASM += "call " + chrom_conv + """
            mov eax, dword [ptr_spectrum]
            """
            lumm = "lumminance" + str(abs(hash(self)))
            self._renderer.converter.Y_asm(lumm, runtimes)
            ASM += "call " + lumm + """
            macro eq32 xmm1 = Y / xmm0
            mov eax, dword [ptr_spectrum]
            macro spectrum eax = xmm1 * eax
            """
        else:
            ASM += """
            macro eq32 xmm0 = x * Y / y 
            macro eq32 xmm1 = Y
            macro eq32 xmm2 = one - x - y
            macro eq32 xmm2 = xmm2 * Y / y
            mov ecx, XYZ
            macro eq32 XYZ = xmm0 {xmm7}
            add ecx, 4
            macro eq32 ecx = xmm1 {xmm7}
            add ecx, 4
            macro eq32 ecx = xmm2 {xmm7}
            macro eq128 xmm0 = XYZ
            """
            xyz_to_rgb = "xyz_to_rgb" + str(abs(hash(self)))
            self._renderer.converter.xyz_to_rgb_asm(xyz_to_rgb, runtimes, self._renderer.assembler)
            ASM += "call " + xyz_to_rgb + """
            mov eax, dword [ptr_spectrum]
            macro eq128 eax.spectrum.values = xmm0 {xmm7}
            """

        ASM += """
        ret

        _angle_calc:
        macro eq32 xmm0 = phi_sun - phi
        macro call fast_cos_ss
        macro eq32 temp1 = xmm0 {xmm7}
        macro eq32 xmm0 = theta_sun
        macro call fast_sin_ss
        macro eq32 temp2 = xmm0 {xmm7}
        macro eq32 xmm0 = theta
        macro call fast_sin_ss
        macro eq32 xmm0 = xmm0 * temp1 * temp2
        macro eq32 temp3 = xmm0 {xmm7}

        macro eq32 xmm0 = theta_sun
        macro call fast_cos_ss
        macro eq32 temp1 = xmm0 {xmm7}
        macro eq32 xmm0 = theta
        macro call fast_cos_ss
        macro eq32 xmm0 = xmm0 * temp1 + temp3
        
        macro eq32 xmm1 = one
        macro if xmm0 > xmm1 goto _gamma_zero
        macro eq32 xmm1 = minus_one
        macro if xmm0 < xmm1 goto _gamma_pi
        macro call fast_acos_ps
        macro eq32 gamma = xmm0 {xmm7}

        ret

        _gamma_zero:
        macro call zero xmm1
        macro eq32 gamma = xmm1 {xmm7}
        ret

        _gamma_pi:
        macro eq32 gamma = PI {xmm7}
        ret

        """
        mc = self._renderer.assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "sky_spectrum" + str(abs(hash(self)))
        for r in runtimes:
            if not r.global_exists(label):
                ds = r.load(name, mc)
                ds['theta_sun'] = self._theta_sun
                ds['phi_sun'] = self._phi_sun
                ds['perez_x'] = tuple(self._perez_x) 
                ds['perez_y'] = tuple(self._perez_y) 
                ds['perez_Y'] = tuple(self._perez_Y) 
                ds['zenith_x'] = self._zenith_x
                ds['zenith_y'] = self._zenith_y
                ds['zenith_Y'] = self._zenith_Y


    # angle bettwen this and sun
    def _angle_beetween(self, thetav, phiv, theta, phi):

        cospsi = sin(thetav) * sin(theta) * cos(phi-phiv) + cos(thetav) * cos(theta)
        if cospsi > 1: return 0.0
        if cospsi < -1: return pi
        return acos(cospsi)
        
    def _perez_function(self, lam, theta, gamma, lvz):
        thetas = self._theta_sun
        den = ((1 + lam[1]*exp(lam[2])) * (1 + lam[3]*exp(lam[4]*thetas) + lam[5]*cos(thetas)*cos(thetas)))

        num = ((1 + lam[1]*exp(lam[2]/cos(theta))) * (1 + lam[3]*exp(lam[4]*gamma)  + lam[5]*cos(gamma)*cos(gamma))) 
        return lvz * num / den

    # eax, ptr to array of coefficients
    # xmm0 - theta
    # xmm1 - gamma
    # xmm2 = zenith
    # xmm3 = theta_sun
    def _perez_function_asm(self, label, runtimes, assembler):
        ASM = """
            #DATA
            float one = 1.0
            float theta, gamma, zenith, theta_sun
            uint32 coeff
            float temp1, temp2
            #CODE
        """
        ASM += " global " + label + ":\n" + """
            mov dword [coeff], eax
            macro eq32 theta = xmm0 {xmm7}
            macro eq32 gamma = xmm1 {xmm7}
            macro eq32 zenith = xmm2 {xmm7}
            macro eq32 theta_sun = xmm3 {xmm7}

            macro eq32 xmm0 = theta_sun
            macro call fast_cos_ss
            mov eax, dword [coeff]
            add eax, 20 
            macro eq32 xmm0 = xmm0 * xmm0 * eax + one
            macro eq32 temp1 = xmm0 {xmm7}
            sub eax, 4
            macro eq32 xmm0 = theta_sun * eax
            macro call fast_exp_ss
            mov eax, dword [coeff]
            add eax, 12
            macro eq32 xmm0 = xmm0 * eax + temp1
            macro eq32 temp1 = xmm0 {xmm7}

            sub eax, 4
            macro eq32 xmm0 = eax
            macro call fast_exp_ss
            mov eax, dword [coeff]
            add eax, 4
            macro eq32 xmm0 = xmm0 * eax + one

            macro eq32 xmm0 = xmm0 * temp1
            macro eq32 temp1 = xmm0 {xmm7}
            ; den = temp1

            macro eq32 xmm0 = gamma
            macro call fast_cos_ss
            mov eax, dword [coeff]
            add eax, 20 
            macro eq32 xmm0 = xmm0 * xmm0 * eax + one
            macro eq32 temp2 = xmm0 {xmm7}

            sub eax, 4
            macro eq32 xmm0 = gamma * eax
            macro call fast_exp_ss
            mov eax, dword [coeff]
            add eax, 12
            macro eq32 xmm0 = xmm0 * eax + temp2
            macro eq32 temp2 = xmm0 {xmm7}

            macro eq32 xmm0 = theta
            macro call fast_cos_ss
            mov eax, dword [coeff]
            add eax, 8 
            macro eq32 xmm1 = eax / xmm0
            macro eq128 xmm0 = xmm1
            macro call fast_exp_ss
            mov eax, dword [coeff]
            add eax, 4
            macro eq32 xmm0 = xmm0 * eax + one
            macro eq32 xmm0 = xmm0 * temp2

            macro eq32 xmm0 = xmm0 * zenith / temp1
            ret
        """
        mc = assembler.assemble(ASM, True)
        name = "perez_function" + str(abs(hash(self)))
        for r in runtimes:
            if not r.global_exists(label):
                ds = r.load(name, mc)

    def L(self, hitpoint, renderer):
        # 1. check visibility
        # 2. populate light vector in hitpoint and spectrum of light

        # 1. generate wi direction
        # sampling hemisphere
        r1 = random()
        r2 = random()

        phi = 2.0 * math.pi * r2
        pu = math.sqrt(1.0 - r1) * math.cos(phi)
        pv = math.sqrt(1.0 - r1) * math.sin(phi)
        pw = math.sqrt(r1)

        w = hitpoint.normal
        tv = Vector3(0.0034, 1.0, 0.0071)
        v = tv.cross(w)
        v.normalize()
        u = v.cross(w)

        wi = u * pu + v * pv + w * pw 
        wi.normalize()

        ndotwi = hitpoint.normal.dot(wi)
        pdf = ndotwi / math.pi 

        hitpoint.wi = wi 
        hitpoint.ndotwi = ndotwi

        if ndotwi < 0.0:
            hitpoint.visible = False
            return False

        t = 50000000.0 # huge t
        dist_point = hitpoint.hit_point + wi * t
        ret = renderer._intersector.visibility(dist_point, hitpoint.hit_point)
        if ret:
            spectrum = self.get_sky_spectrum(wi)
            hitpoint.l_spectrum = spectrum * (1.0 / pdf)
            hitpoint.visible = True
            return True
        else:
            hitpoint.visible = False
            return False

    def Le(self, direction):
        s = self.get_sky_spectrum(direction)
        return s 

    # in xmm0 is direction of ray
    def Le_asm(self, runtimes, assembler, structures, label):
        sky_spectrum = "sky_spectrum" + str(abs(hash(self)))
        self.get_sky_spectrum_asm(sky_spectrum, runtimes)
        code = """
            #DATA
        """
        code += structures.structs(('hitpoint',)) + """
            spectrum ret_spectrum 
            #CODE
        """
        code += "global " + label + ":\n"
        code += """
            mov eax, ret_spectrum
        """
        code += "call " + sky_spectrum + """
            mov eax, ret_spectrum 
            ret
        """
        mc = assembler.assemble(code, True)
        name = "evironment_const" + str(abs(hash(self)))
        self._ds = []
        for r in runtimes:
            ds = r.load(name, mc)
            ds["ret_spectrum.values"] = self._renderer.converter.zero_spectrum().to_ds()
            self._ds.append(ds)

    #eax - pointer to hitpoint structure
    def L_asm(self, runtimes, visible_label, assembler, structures):
        sky_spectrum = "sky_spectrum" + str(abs(hash(self)))
        self.get_sky_spectrum_asm(sky_spectrum, runtimes)

        if proc.AVX:
            line1 = "vmovss xmm1, dword [ecx + 4*ebx] \n"
        else:
            line1 = "movss xmm1, dword [ecx + 4*ebx] \n"

        code = """
            #DATA
        """
        code += structures.structs(('hitpoint',)) + """
        spectrum l_spectrum
        float pi[4] = 3.14159265359, 3.14159265359, 3.14159265359, 3.14159265359
        float one[4] = 1.0, 1.0, 1.0, 1.0
        float two[4] = 2.0, 2.0, 2.0, 2.0
        float tvector[4] = 0.0034, 1.0, 0.0071, 0.0

        float pu[4]
        float pv[4]
        float pw[4]
        float t[4] = 50000000.0, 50000000.0, 50000000.0, 0.0

        uint32 ptr_hp
        uint32 idx = 0

        #CODE

            mov dword [ptr_hp], eax
            sub dword [idx], 1
            js _calculate_samples
            _gen_direction:
            mov eax, dword [ptr_hp]
            macro eq128 xmm1 = eax.hitpoint.normal {xmm1}
            macro eq128 xmm7 = xmm1
            macro eq128 xmm0 = tvector
            macro cross xmm0 x xmm1 {xmm2, xmm3}
            macro normalization xmm0 {xmm1, xmm2}
            macro eq128 xmm1 = xmm7
            macro eq128 xmm6 = xmm0
            macro cross xmm0 x xmm1 {xmm2, xmm3}
            mov ebx, dword [idx]
            mov ecx, pu
            ; in line we load pu, pv or pw

            """
        code += line1 + """
            macro broadcast xmm1 = xmm1[0]
            macro eq128 xmm0 = xmm0 * xmm1
            mov ecx, pv
        """
        code += line1 + """
            macro broadcast xmm1 = xmm1[0]
            macro eq128 xmm6 = xmm6 * xmm1
            macro eq128 xmm0 = xmm0 + xmm6
            mov ecx, pw
        """
        code += line1 + """
            macro broadcast xmm1 = xmm1[0]
            macro eq128 xmm1 = xmm1 * xmm7
            macro eq128 xmm0 = xmm0 + xmm1
            macro normalization xmm0 {xmm1, xmm2}
            macro dot xmm1 = xmm0 * xmm7 {xmm3, xmm4}
            ; wi - xmm0, ndotwi - xmm1
        
        mov eax, dword [ptr_hp]
        macro dot xmm2 = xmm0 * eax.hitpoint.normal {xmm6, xmm7}
        macro call zero xmm5
        macro if xmm2 < xmm5 goto reject  

        macro eq128 eax.hitpoint.wi = xmm0 {xmm0}
        macro eq32 eax.hitpoint.ndotwi = xmm1 {xmm1}
        ; test visibility of two points
        
        macro eq128 xmm0 = xmm0 * t + eax.hitpoint.hit
        macro eq128 xmm1 = eax.hitpoint.hit
        """
        code += "call " + visible_label + "\n" + """
        cmp eax, 1
        jne reject

        mov ecx, dword [ptr_hp]
        macro eq128 xmm0 = ecx.hitpoint.wi
        mov eax, l_spectrum
        """
        code += "call " + sky_spectrum + """

        mov eax, dword [ptr_hp]
        mov dword [eax + hitpoint.visible], 1
        lea ecx, dword [eax + hitpoint.l_spectrum]
        mov ebx, l_spectrum
        macro eq32 xmm0 = pi / eax.hitpoint.ndotwi
        macro spectrum ecx = xmm0 * ebx
        ret

        reject:
        mov eax, dword [ptr_hp]
        mov dword [eax + hitpoint.visible], 0
        ret

        _calculate_samples:
            macro call random 
            macro eq128 xmm1 = one - xmm0

        """
        if proc.AVX:
            code += "vsqrtps xmm0, xmm0 \n"
            code += "vsqrtps xmm1, xmm1 \n"
        else:
            code += "sqrtps xmm0, xmm0 \n"
            code += "sqrtps xmm1, xmm1 \n"

        code += """
            macro eq128 pw = xmm0 {xmm0}
            macro eq128 pu = xmm1 {xmm0}
            macro eq128 pv = xmm1 {xmm0}

            macro call random 

            macro eq128 xmm0 = xmm0 * pi * two
            macro call fast_sincos_ps
            macro eq128 xmm6 = xmm6 * pu
            macro eq128 xmm0 = xmm0 * pv

            macro eq128 pu = xmm6  {xmm6}
            macro eq128 pv = xmm0  {xmm0}
            mov dword [idx], 3
            jmp _gen_direction 
        """

        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        self.l_asm_name = name = "environment_sun_L" + str(hash(self))
        for r in runtimes:
            ds = r.load(name, mc)

    def convert_spectrums(self, converter):
        pass


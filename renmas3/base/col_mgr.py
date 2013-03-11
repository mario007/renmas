
import platform
import renmas3.switch as proc
from .spectrum import Spectrum, RGBSpectrum, SampledSpectrum
from ..macros import MacroSpectrum, create_assembler

from .cie_consts import Cie_x, Cie_y, Cie_z, SpectWhite, SpectCyan, SpectMagenta
from .cie_consts import SpectYellow, SpectRed, SpectGreen, SpectBlue, IllumSpectWhite
from .cie_consts import IllumSpectCyan, IllumSpectMagenta, IllumSpectYellow
from .cie_consts import IllumSpectRed, IllumSpectGreen, IllumSpectBlue, S0, S1, S2

## Class that is used for manipulation of spectrums(colors). 
# One of the main usage of this class is to create spectrum(color).
# Color can be represent with intesities at specified wavelength or
# just with three basic component r, g, b.
# Default mode is spectrum mode where color is represent
# with 32 intesities in 400-700nm range of spectrum. 

#TODO extarct all required parameters and make function that create
# samples for sampled spectrum beacause it can be useful outside
# of ColorManager
class ColorManager:
    def __init__(self, spectral=True):

        self._bits = platform.architecture()[0]

        self._spectral = spectral
        self._spectrum_region = (400, 700)
        self._nsamples = 32
        
        self._assembler = create_assembler()
        self._macro_spectrum = MacroSpectrum(self)
        self._assembler.register_macro('spectrum', self._macro_spectrum.macro_spectrum)

        self._create_spectrums()

    @property
    def spectral(self):
        return self._spectral

    @property
    def nsamples(self):
        return self._nsamples

    def _create_spectrums(self):
        self._cie_x = self._create_sampled_spectrum(Cie_x)
        self._cie_y = self._create_sampled_spectrum(Cie_y)
        self._cie_z = self._create_sampled_spectrum(Cie_z)
        self.yint= sum(self._cie_y.samples)

        self._spect_white = self._create_sampled_spectrum(SpectWhite)
        self._spect_cyan = self._create_sampled_spectrum(SpectCyan)
        self._spect_magenta = self._create_sampled_spectrum(SpectMagenta)
        self._spect_yellow = self._create_sampled_spectrum(SpectYellow)
        self._spect_red = self._create_sampled_spectrum(SpectRed)
        self._spect_green = self._create_sampled_spectrum(SpectGreen)
        self._spect_blue = self._create_sampled_spectrum(SpectBlue)

        self._illum_spect_white = self._create_sampled_spectrum(IllumSpectWhite)
        self._illum_spect_cyan = self._create_sampled_spectrum(IllumSpectCyan)
        self._illum_spect_magenta = self._create_sampled_spectrum(IllumSpectMagenta)
        self._illum_spect_yellow = self._create_sampled_spectrum(IllumSpectYellow)
        self._illum_spect_red = self._create_sampled_spectrum(IllumSpectRed)
        self._illum_spect_green = self._create_sampled_spectrum(IllumSpectGreen)
        self._illum_spect_blue = self._create_sampled_spectrum(IllumSpectBlue)

        self._s0 = self._create_sampled_spectrum(S0)
        self._s1 = self._create_sampled_spectrum(S1)
        self._s2 = self._create_sampled_spectrum(S2)

    ## Create spectrum from samples  
    # @param self The object pointer
    # @param vals This is list of samples and each sample is represent with
    # tuple [(wavelength, intesity), ...] 
    # @return Return spectrum 
    def _create_sampled_spectrum(self, vals):
        samples = self._create_samples(vals)
        return SampledSpectrum(samples)

    ## Create list of intesities form list of samples.
    # One sample is represented with tuple (wavelength, intesity)
    # @param self The object pointer
    # @param vals List of samples
    # @return Return list of intesities 
    def _create_samples(self, vals):
        nspec = self._nsamples
        start, end = self._spectrum_region
        s = []
        for i in range(nspec):
            lambda0 = self.lerp(float(i)/float(nspec), start, end)
            lambda1 = self.lerp(float(i+1)/float(nspec), start, end)
            s.append(self._average_spectrum(vals, lambda0, lambda1))
        return s

    ## linear intepolation
    #
    def lerp(self, t, v1, v2):
        return (1.0 - t) * v1 + t * v2

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

    ## Create spectrum form samples.
    # @param self The object pointer
    # @param vals List of samples. If you want to create spectrum from r,g,b components
    # than pass tuple (r, g, b). If you want to create spectrum from intesities 
    # than pass list of samples where each sample is represented with tuple (wavelength, intesity)
    # @param illum Create spectrum for illuminat(light). Default is for reflectance.
    # @return Return spectrum 
    def create_spectrum(self, vals, illum=False):
        if self._spectral:
            if len(vals) == 3:
                if type(vals[0]) == tuple:
                    return self._create_sampled_spectrum(vals)
                else:
                    return self.rgb_to_sampled(vals, illum)
            else:
                return self._create_sampled_spectrum(vals)
        else:
            if len(vals) == 3:
                if type(vals[0]) == tuple:
                    s = self._create_sampled_spectrum(vals)
                    return self.to_RGB(s)
                else:
                    r, g, b = float(vals[0]), float(vals[1]), float(vals[2])
                    return RGBSpectrum(r, g, b)
            else:
                s = self._create_sampled_spectrum(vals)
                return self.to_RGB(s)

    ## Convert rgb components to sampled Spectrum.
    # @param self The object pointer
    # @param values tuple with r,g,b components
    # @param illum convert spectrum for illuminat
    # @return Return spectrum 
    def rgb_to_sampled(self, values, illum=False):
        if len(values) != 3: raise ValueError("We need just 3 rgb values!!!") 
        r, g, b = values
        if illum:
            #conversion of illuminat 
            if r <= g and r <= b:
                # Compute illuminant with red as minimum
                rez = r * self._illum_spect_white
                if g <= b:
                    rez += (g - r) * self._illum_spect_cyan
                    rez += (b - g) * self._illum_spect_blue
                else:
                    rez += (b - r) * self._illum_spect_cyan
                    rez += (g - b) * self._illum_spect_green
            elif g <= r and g <= b:
                # Compute illuminant with green as minimum
                rez = g * self._illum_spect_white
                if r <= b:
                    rez += (r - g) * self._illum_spect_magenta
                    rez += (b - r) * self._illum_spect_blue
                else:
                    rez += (b - g) * self._illum_spect_magenta
                    rez += (r - b) * self._illum_spect_red
            else:
                # Compute illuminant with blue as minimum
                rez = b * self._illum_spect_white
                if r <= g:
                    rez += (r - b) * self._illum_spect_yellow
                    rez += (g - r) * self._illum_spect_green
                else:
                    rez += (g - b) * self._illum_spect_yellow
                    rez += (r - g) * self._illum_spect_red
            rez = rez * 0.86445
        else:
            #conversion of reflectance 
            if r <= g and r <= b:
                # Compute illuminant with red as minimum
                rez = r * self._spect_white
                if g <= b:
                    rez += (g - r) * self._spect_cyan
                    rez += (b - g) * self._spect_blue
                else:
                    rez += (b - r) * self._spect_cyan
                    rez += (g - b) * self._spect_green
            elif g <= r and g <= b:
                # Compute illuminant with green as minimum
                rez = g * self._spect_white
                if r <= b:
                    rez += (r - g) * self._spect_magenta
                    rez += (b - r) * self._spect_blue
                else:
                    rez += (b - g) * self._spect_magenta
                    rez += (r - b) * self._spect_red
            else:
                # Compute illuminant with blue as minimum
                rez = b * self._spect_white
                if r <= g:
                    rez += (r - b) * self._spect_yellow
                    rez += (g - r) * self._spect_green
                else:
                    rez += (g - b) * self._spect_yellow
                    rez += (r - g) * self._spect_red
            rez = rez * 0.94
        rez.clamp()
        return rez

    # Convert spectrum to r,g,b components
    # @param self The object pointer
    # @param spectrum   
    # @return spectrum Return RGBSpectrum
    def to_RGB(self, spectrum):
        if isinstance(spectrum, RGBSpectrum):
            return RGBSpectrum(spectrum.r, spectrum.g, spectrum.b)
        X, Y, Z = self.to_XYZ(spectrum)
        r, g, b = self.XYZ_to_RGB(X, Y, Z)
        return RGBSpectrum(r, g, b)

    def to_RGB_asm(self, runtimes):
        # in eax(rax) must be spectrum
        if self._spectral:
            self.XYZ_to_RGB_asm(runtimes)
            ASM = " #DATA \n" + self.spectrum_asm_struct() + """
                Spectrum __x, __y, __z, temp
                float one_over_yint
                float XYZ[4]
                #CODE
                global spectrum_to_rgb:
                macro mov ebx, __x
                macro mov ecx, temp
                macro spectrum ecx = eax * ebx
                macro spectrum sum ecx
                macro eq32 XYZ = xmm0 * one_over_yint {xmm1}
                macro mov ebx, __y
                macro spectrum ecx = eax * ebx
                macro spectrum sum ecx
                macro eq32 xmm0 = xmm0 * one_over_yint
            """
            if proc.AVX:
                ASM += "vmovss dword [XYZ + 4], xmm0 \n"
            else:
                ASM += "movss dword [XYZ + 4], xmm0 \n"
            ASM += """
                macro mov ebx, __z
                macro spectrum ecx = eax * ebx
                macro spectrum sum ecx
                macro eq32 xmm0 = xmm0 * one_over_yint {xmm1}
                """
            if proc.AVX:
                ASM += "vmovss dword [XYZ + 8], xmm0 \n"
            else:
                ASM += "movss dword [XYZ + 8], xmm0 \n"
            ASM += """
                macro eq128 xmm0 = XYZ 
                call XYZ_to_RGB
                ret
            """
            descs = []
            mc = self._assembler.assemble(ASM, True)
            #mc.print_machine_code()
            name = "spectrum_to_rgb" + str(id(self))
            for r in runtimes:
                if not r.global_exists('spectrum_to_rgb'):
                    descs.append(r.load(name, mc))
            for ds in descs:
                ds["one_over_yint"] = 1.0 / self.yint
                ds["__x.values"] = self._cie_x.to_ds()
                ds["__y.values"] = self._cie_y.to_ds()
                ds["__z.values"] = self._cie_z.to_ds()

        else:
            ASM = " #DATA \n" + self.spectrum_asm_struct() + """
                #CODE
                global spectrum_to_rgb:
                macro eq128 xmm0 = eax.Spectrum.values
                ret
            """
            mc = self._assembler.assemble(ASM, True)
            #mc.print_machine_code()
            name = "spectrum_to_rgb" + str(id(self))
            for r in runtimes:
                if not r.global_exists('spectrum_to_rgb'):
                    r.load(name, mc)

    # Convert spectrum to X,Y,Z components
    # @param self The object pointer
    # @param spectrum   
    # @return spectrum Return (X, Y, Z)
    def to_XYZ(self, spectrum):
        if isinstance(spectrum, RGBSpectrum):
            return RGB_to_XYZ(spectrum.r, spectrum.g, spectrum.b)

        x = self._cie_x.mix_spectrum(spectrum)
        y = self._cie_y.mix_spectrum(spectrum)
        z = self._cie_z.mix_spectrum(spectrum)
        x_sum = sum(x.samples)
        y_sum = sum(y.samples)
        z_sum = sum(z.samples)

        X = x_sum / self.yint  
        Y = y_sum / self.yint  
        Z = z_sum / self.yint  
        return (X, Y, Z)

    # Calcualte lumminance of spectrum 
    # @param self The object pointer
    # @param spectrum   
    # @return Lumminance of spectrum
    def Y(self, spectrum):
        if isinstance(spectrum, RGBSpectrum):
            return spectrum.r*0.212671 + spectrum.g*0.715160 + spectrum.b*0.072169
        y = self._cie_y.mix_spectrum(spectrum)
        y_sum = sum(y.samples)
        return y_sum / self.yint  

    def _Y_asm_rgb(self, runtimes):
        ASM = " #DATA \n" + self.spectrum_asm_struct() + """
            float lumm[4] = 0.212671, 0.715160, 0.072169, 0.0
            #CODE
            global lumminance:
            macro eq128 xmm0 = eax.Spectrum.values
            macro dot xmm0 = xmm0 * lumm {xmm6, xmm7}
            ret
        """
        mc = self._assembler.assemble(ASM, True)
        name = "Y_lumm" + str(id(self))
        for r in runtimes:
            if not r.global_exists('lumminance'):
                r.load(name, mc)
    
    def _Y_asm_spectrum(self, runtimes):
        ASM = " #DATA \n" + self.spectrum_asm_struct() + """
            Spectrum __y, temp
            float one_over_yint
            #CODE
            global lumminance:
            macro mov ebx, __y
            macro mov ecx, temp
            macro spectrum ecx = eax * ebx
            macro spectrum sum ecx
            macro eq32 xmm0 = xmm0 * one_over_yint 
            ret

        """
        mc = self._assembler.assemble(ASM, True)
        name = "Y_lumm" + str(id(self))
        dsecs = []
        for r in runtimes:
            if not r.global_exists('lumminance'):
                dsecs.append(r.load(name, mc))
        for ds in dsecs:
            ds["one_over_yint"] = 1.0 / self.yint
            ds["__y.values"] = self._cie_y.to_ds()

    def Y_asm(self, runtimes):
        if self._spectral:
            self._Y_asm_spectrum(runtimes)
        else:
            self._Y_asm_rgb(runtimes)

    def XYZ_to_RGB(self, X, Y, Z):
        r = 3.240479 * X - 1.537150 * Y - 0.498535 * Z
        g = -0.969256 * X + 1.875991 * Y + 0.041556 * Z
        b = 0.055648 * X - 0.204043 * Y + 1.057311 * Z
        return (r, g, b)

    def XYZ_to_RGB_asm(self, runtimes):
        ASM = """
            #DATA
            float coff1[4] = 3.240479, -0.969256, 0.055648, 0.0
            float coff2[4] = -1.537150, 1.875991, -0.204043, 0.0
            float coff3[4] = -0.498535, 0.041556, 1.057311, 0.0
            #CODE
            global XYZ_to_RGB:
            macro broadcast xmm1 = xmm0[0]
            macro eq128 xmm1 = xmm1 * coff1
            macro broadcast xmm2 = xmm0[1]
            macro eq128 xmm2 = xmm2 * coff2
            macro eq128 xmm5 = xmm1 + xmm2
            macro broadcast xmm3 = xmm0[2]
            macro eq128 xmm3 = xmm3 * coff3
            macro eq128 xmm0 = xmm5 + xmm3
            ret
        """
        mc = self._assembler.assemble(ASM, True)
        name = "XYZ_to_RGB" + str(id(self))
        for r in runtimes:
            if not r.global_exists('XYZ_to_RGB'):
                ds = r.load(name, mc)

    def RGB_to_XYZ(self, r, g, b):
        X = 0.412453 * r + 0.357580 * g + 0.180423 * b
        Y = 0.212671 * r + 0.715160 * g + 0.072169 * b
        Z = 0.019334 * r + 0.119193 * g + 0.950227 * b 
        return (X, Y, Z)

    # Return code for assembly struct of spectrum
    #
    def spectrum_asm_struct(self):
        code = "struct Spectrum \n"
        if self._spectral:
            code += "float values[ %i ] \n" % self._nsamples
        else:
            code += "float values[4] \n"
        code += "end struct \n"
        return code

    # Return wavelengths
    #
    def wavelengths(self):
        start, end = self._spectrum_region
        w = []
        for i in range(self._nsamples):
            lambda0 = self.lerp(float(i)/float(self._nsamples), start, end)
            lambda1 = self.lerp(float(i+1)/float(self._nsamples), start, end)
            w.append(0.5*(lambda1+lambda0))
        return w

    # Return wavelengths intervals
    #
    def wavelength_intervals(self):
        start, end = self._spectrum_region
        intervals = []
        for i in range(self._nsamples):
            lambda0 = self.lerp(float(i)/float(self._nsamples), start, end)
            lambda1 = self.lerp(float(i+1)/float(self._nsamples), start, end)
            intervals.append((lambda0, lambda1))
        return intervals

    def convert_spectrum(self, spectrum, illum=False):
        #TODO -- resampled spectrum 

        if self._spectral:
            if isinstance(spectrum, SampledSpectrum):
                return spectrum
            else:
                return self.create_spectrum((spectrum.r, spectrum.g, spectrum.b), illum)
        else:
            if isinstance(spectrum, SampledSpectrum):
                return self.to_RGB(spectrum)
            else:
                return spectrum

    def black(self):
        if self._spectral:
            return SampledSpectrum([0.0]*self._nsamples)
        else:
            return RGBSpectrum(0.0, 0.0, 0.0)

    def load_asm_function(self, func_name, runtimes):
        if func_name == "spectrum_to_rgb":
            self.to_RGB_asm(runtimes)
        else:
            raise ValueError("Cannot load asm function ", func_name)

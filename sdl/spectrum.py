
"""
    This module contain implementation of basic spectrum types.
"""

from .cie_consts import Cie_x, Cie_y, Cie_z, SpectWhite, SpectCyan,\
    SpectYellow, SpectRed, SpectGreen, SpectBlue, IllumSpectWhite,\
    SpectMagenta, IllumSpectCyan, IllumSpectMagenta, IllumSpectYellow,\
    IllumSpectRed, IllumSpectGreen, IllumSpectBlue


class Spectrum:
    """
        Abstract base class for spectrum.
    """
    def __init__(self):
        pass

    def __add__(self, spectrum):
        """
            Return sum of two spectrums.
        """
        raise NotImplementedError()

    def __sub__(self, spectrum):
        """
            Return substraction of two spectrums.
        """
        raise NotImplementedError()

    def __mul__(self, t):
        """
            Return new spectrum that is scaled by factor t.
        """
        raise NotImplementedError()

    def __rmul__(self, t):
        """
            Return new spectrum that is scaled by factor t.
        """
        raise NotImplementedError()

    def __truediv__(self, spectrum):
        """
            Divide components of two spectrums.
        """
        raise NotImplementedError()

    def clamp(self, low=0.0, high=100000000.0):
        """
            Clamp each component of spectrum in range [low, high].
        """
        raise NotImplementedError()

    def scale(self, t):
        """
            Inplace scale each component of spectrum by factor t.
        """
        raise NotImplementedError()

    def zero(self):
        """
            Return new zero spectrum.
        """
        raise NotImplementedError()

    def set(self, value):
        """
            Set each component of spectrum to value.
        """
        raise NotImplementedError()


class RGBSpectrum(Spectrum):

    __slots__ = ['r', 'g', 'b']

    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __str__(self):
        """
            Return information about RGBSpectrum.
        """
        return '(%s,%s,%s)' % (self.r, self.g, self.b)

    def __repr__(self):
        """
            Return information about RGBSpectrum.
        """
        return 'Spectrum(%s,%s,%s)' % (self.r, self.g, self.b)

    def __add__(self, spectrum):
        return RGBSpectrum(self.r + spectrum.r, self.g + spectrum.g, self.b + spectrum.b)

    def __sub__(self, spectrum):
        return RGBSpectrum(self.r - spectrum.r, self.g - spectrum.g, self.b - spectrum.b)

    def __mul__(self, t):
        if isinstance(t, RGBSpectrum):
            return RGBSpectrum(self.r * t.r, self.g * t.g, self.b * t.b)
        return RGBSpectrum(self.r * t, self.g * t, self.b * t)

    def __rmul__(self, t):
        if isinstance(t, RGBSpectrum):
            return RGBSpectrum(self.r * t.r, self.g * t.g, self.b * t.b)
        return RGBSpectrum(self.r * t, self.g * t, self.b * t)

    def __truediv__(self, spectrum):
        """
            Divide components of spectrums.
        """
        epsilon = 1e-15
        r = spectrum.r
        g = spectrum.g
        b = spectrum.b
        if r < epsilon:
            r = epsilon
        if g < epsilon:
            g = epsilon
        if b < epsilon:
            b = epsilon
        return RGBSpectrum(self.r / r, self.g / g, self.b / b)

    def scale(self, t):
        """
            Inplace scale each component of spectrum by factor t.
        """
        self.r = t * self.r
        self.g = t * self.g
        self.b = t * self.b
        return self

    def clamp(self, low=0.0, high=100000000.0):
        """
            Clamp each component of spectrum in range [low, high].
        """
        if self.r > high:
            self.r = high
        if self.g > high:
            self.g = high
        if self.b > high:
            self.b = high
        if self.r < low:
            self.r = low
        if self.g < low:
            self.g = low
        if self.b < low:
            self.b = low

    def zero(self):
        return RGBSpectrum(0.0, 0.0, 0.0)

    def set(self, value):
        value = float(value)
        self.r = value
        self.g = value
        self.b = value
        return self


class SampledSpectrum(Spectrum):

    __slots__ = ['samples']

    def __init__(self, samples):
        self.samples = samples

    def __str__(self):
        return str(self.samples)

    def __repr__(self):
        return str(self.samples)

    def __add__(self, spectrum):
        samples = [self.samples[i] + spectrum.samples[i] for i in range(len(self.samples))]
        return SampledSpectrum(samples)

    def __sub__(self, spectrum):
        samples = [self.samples[i] - spectrum.samples[i] for i in range(len(self.samples))]
        return SampledSpectrum(samples)

    def __mul__(self, t):
        if isinstance(t, SampledSpectrum):
            samples = [self.samples[i] * t.samples[i] for i in range(len(self.samples))]
            return SampledSpectrum(samples)
        samples = [self.samples[i] * t for i in range(len(self.samples))]
        return SampledSpectrum(samples)

    def __rmul__(self, t):
        if isinstance(t, SampledSpectrum):
            samples = [self.samples[i] * t.samples[i] for i in range(len(self.samples))]
            return SampledSpectrum(samples)
        samples = [self.samples[i] * t for i in range(len(self.samples))]
        return SampledSpectrum(samples)

    def __truediv__(self, spectrum):
        """
            Divide components of spectrums.
        """
        epsilon = 1e-15
        samples = []
        for i in range(len(self.samples)):
            c = spectrum.samples[i]
            if c < epsilon:
                c = epsilon
            samples.append(self.samples[i] / c)
        return SampledSpectrum(samples)

    def scale(self, t):
        """
            Inplace scale each component of spectrum by factor t.
        """
        self.samples = [self.samples[i] * t for i in range(len(self.samples))]
        return self

    def clamp(self, low=0.0, high=100000000.0):
        """
            Clamp each component of spectrum in range [low, high].
        """
        for i in range(len(self.samples)):
            if self.samples[i] > high:
                self.samples[i] = high
            if self.samples[i] < low:
                self.samples[i] = low

    def zero(self):
        vals = [0.0 for i in range(len(self.samples))]
        return SampledSpectrum(vals)

    def set(self, value):
        value = float(value)
        self.samples = [value for i in range(len(self.samples))]
        return self


def lerp(t, v1, v2):
    return (1.0 - t) * v1 + t * v2


def average_spectrum(vals, lambda1, lambda2):

    # out of bounds or single value
    lam1, val1 = vals[0]
    if lambda2 <= lam1:
        return val1
    lam2, val2 = vals[-1]
    if lambda1 >= lam2:
        return val2
    if len(vals) == 1:
        return val1

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
        return lerp((w-vals[i][0])/(vals[i+1][0]-vals[i][0]), vals[i][1], vals[i+1][1])

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


def create_samples(vals, nsamples, start, end):
    s = []
    for i in range(nsamples):
        lambda0 = lerp(float(i) / float(nsamples), start, end)
        lambda1 = lerp(float(i+1) / float(nsamples), start, end)
        s.append(average_spectrum(vals, lambda0, lambda1))
    return s


class SampledManager:
    def __init__(self, nsamples=32, start=400, end=700):

        self.nsamples = nsamples
        self.start = start
        self.end = end

        self._create_spectrums()

    ## Create spectrum from samples
    # @param self The object pointer
    # @param vals This is list of samples and each sample is represent with
    # tuple [(wavelength, intesity), ...]
    # @return Return spectrum
    def _create_sampled_spectrum(self, vals):
        samples = create_samples(vals, self.nsamples, self.start, self.end)
        return SampledSpectrum(samples)

    def _create_spectrums(self):
        self._cie_x = self._create_sampled_spectrum(Cie_x)
        self._cie_y = self._create_sampled_spectrum(Cie_y)
        self._cie_z = self._create_sampled_spectrum(Cie_z)
        self.yint = 106.856895
        #yint = CIE_Y_integral

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

    def luminance(self, spectrum):
        if not isinstance(spectrum, SampledSpectrum):
            raise ValueError("SampledSpectrum is expected!", spectrum)
        y = self._cie_y * spectrum
        y_sum = sum(y.samples)

        #yint = CIE_Y_integral
        scale = float(self.end - self.start) / (self.yint * self.nsamples)
        return y_sum * scale

    def rgb_to_sampled(self, spectrum, illum=False):
        if not isinstance(spectrum, RGBSpectrum):
            raise ValueError("RGBSpectrum is expected!", spectrum)
        r = spectrum.r
        g = spectrum.g
        b = spectrum.b
        if illum:
            # conversion of illuminat
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
            # conversion of reflectance
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

    def sampled_to_rgb(self, spectrum):
        if not isinstance(spectrum, SampledSpectrum):
            raise ValueError("Sampled spectrum is expected!", spectrum)

        x = self._cie_x * spectrum
        y = self._cie_y * spectrum
        z = self._cie_z * spectrum
        x_sum = sum(x.samples)
        y_sum = sum(y.samples)
        z_sum = sum(z.samples)

        #yint = CIE_Y_integral
        scale = float(self.end - self.start) / (self.yint * self.nsamples)

        X = x_sum * scale
        Y = y_sum * scale
        Z = z_sum * scale

        r, g, b = self.xyz_to_rgb(X, Y, Z)
        return RGBSpectrum(r, g, b)

    def xyz_to_rgb(self, X, Y, Z):
        r = 3.240479 * X - 1.537150 * Y - 0.498535 * Z
        g = -0.969256 * X + 1.875991 * Y + 0.041556 * Z
        b = 0.055648 * X - 0.204043 * Y + 1.057311 * Z
        return (r, g, b)

    def rgb_to_xyz(self, r, g, b):
        X = 0.412453 * r + 0.357580 * g + 0.180423 * b
        Y = 0.212671 * r + 0.715160 * g + 0.072169 * b
        Z = 0.019334 * r + 0.119193 * g + 0.950227 * b
        return (X, Y, Z)

    def convert_spectrum(self, spectrum, illum=False):
        if isinstance(spectrum, RGBSpectrum):
            return self.rgb_to_sampled(spectrum, illum=illum)
        elif isinstance(spectrum, SampledSpectrum):
            return SampledSpectrum(tuple(spectrum.samples))
        else:
            raise ValueError("Unknown spectrum type", spectrum)

    def zero(self):
        vals = [0.0 for i in range(self.nsamples)]
        return SampledSpectrum(vals)


class RGBManager:
    def __init__(self, nsamples=32, start=400, end=700):

        self.nsamples = nsamples
        self.start = start
        self.end = end

        self._create_spectrums()

    ## Create spectrum from samples
    # @param self The object pointer
    # @param vals This is list of samples and each sample is represent with
    # tuple [(wavelength, intesity), ...]
    # @return Return spectrum
    def _create_sampled_spectrum(self, vals):
        samples = create_samples(vals, self.nsamples, self.start, self.end)
        return SampledSpectrum(samples)

    def _create_spectrums(self):
        self._cie_x = self._create_sampled_spectrum(Cie_x)
        self._cie_y = self._create_sampled_spectrum(Cie_y)
        self._cie_z = self._create_sampled_spectrum(Cie_z)
        self.yint = 106.856895
        #yint = CIE_Y_integral

    def luminance(self, spectrum):
        if not isinstance(spectrum, RGBSpectrum):
            raise ValueError("RGBSpectrum is expected!", spectrum)
        return spectrum.r * 0.212671 + spectrum.g * 0.715160 + spectrum.b * 0.072169

    def xyz_to_rgb(self, X, Y, Z):
        r = 3.240479 * X - 1.537150 * Y - 0.498535 * Z
        g = -0.969256 * X + 1.875991 * Y + 0.041556 * Z
        b = 0.055648 * X - 0.204043 * Y + 1.057311 * Z
        return (r, g, b)

    def rgb_to_xyz(self, r, g, b):
        X = 0.412453 * r + 0.357580 * g + 0.180423 * b
        Y = 0.212671 * r + 0.715160 * g + 0.072169 * b
        Z = 0.019334 * r + 0.119193 * g + 0.950227 * b
        return (X, Y, Z)

    def sampled_to_rgb(self, spectrum):
        if not isinstance(spectrum, SampledSpectrum):
            raise ValueError("Sampled spectrum is expected!", spectrum)

        x = self._cie_x * spectrum
        y = self._cie_y * spectrum
        z = self._cie_z * spectrum
        x_sum = sum(x.samples)
        y_sum = sum(y.samples)
        z_sum = sum(z.samples)

        #yint = CIE_Y_integral
        scale = float(self.end - self.start) / (self.yint * self.nsamples)

        X = x_sum * scale
        Y = y_sum * scale
        Z = z_sum * scale

        r, g, b = self.xyz_to_rgb(X, Y, Z)
        return RGBSpectrum(r, g, b)

    def convert_spectrum(self, spectrum, illum=False):
        if isinstance(spectrum, RGBSpectrum):
            return RGBSpectrum(spectrum.r, spectrum.g, spectrum.b)
        elif isinstance(spectrum, SampledSpectrum):
            return self.sampled_to_rgb(spectrum)
        else:
            raise ValueError("Unknown spectrum type", spectrum)

    def zero(self):
        return RGBSpectrum(0.0, 0.0, 0.0)

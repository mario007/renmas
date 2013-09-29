
"""
    This module contain implementation of basic spectrum types.
"""


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

    def mix(self, spectrum):
        """
            Multiply components of two spectrums.
        """
        raise NotImplementedError()

    def divide(self, spectrum):
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

    def asm_struct(self):
        """
            Return struct definition of Spectrum for tdasm.
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
            return self.mix(t)
        return RGBSpectrum(self.r * t, self.g * t, self.b * t)

    def __rmul__(self, t):
        if isinstance(t, RGBSpectrum):
            return self.mix(t)
        return RGBSpectrum(self.r * t, self.g * t, self.b * t)

    def mix(self, spectrum):
        """
            Mix two spectrums by multiplying their components.
        """
        return RGBSpectrum(self.r * spectrum.r, self.g * spectrum.g, self.b * spectrum.b)

    def divide(self, spectrum):
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
        if self.r > high: self.r = high 
        if self.g > high: self.g = high 
        if self.b > high: self.b = high 
        if self.r < low: self.r = low 
        if self.g < low: self.g = low 
        if self.b < low: self.b = low 

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
            return self.mix(t)
        samples = [self.samples[i] * t for i in range(len(self.samples))]
        return SampledSpectrum(samples)

    def __rmul__(self, t):
        if isinstance(t, SampledSpectrum):
            return self.mix(t)
        samples = [self.samples[i] * t for i in range(len(self.samples))]
        return SampledSpectrum(samples)

    def mix(self, spectrum):
        """
            Mix two spectrums by multiplying their components.
        """
        samples = [self.samples[i] * spectrum.samples[i] for i in range(len(self.samples))]
        return SampledSpectrum(samples)

    def divide(self, spectrum):
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

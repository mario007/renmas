
class Spectrum:
    def __init__(self):
        pass

    def __add__(self, spectrum):
        NotImplementedError()

    def __sub__(self, spectrum):
        NotImplementedError()

    def __mul__(self, t):
        NotImplementedError()

    def __rmul__(self, t):
        NotImplementedError()

    def mix_spectrum(self, spectrum):
        NotImplementedError()

    def clamp(self, low=0.0, high=100000000.0):
        NotImplementedError()

    def black(self):
        NotImplementedError()

    def set(self, value):
        NotImplementedError()

    def to_ds(self):
        NotImplementedError()

    def asm_struct(self):
        NotImplementedError()

class RGBSpectrum(Spectrum):
    __slots__ = ['r', 'g', 'b']
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __str__(self):
        return '(%s,%s,%s)' % (self.r, self.g, self.b)

    def __repr__(self):
        return 'Spectrum(%s,%s,%s)' % (self.r, self.g, self.b)

    def __add__(self, spectrum):
        return RGBSpectrum(self.r + spectrum.r, self.g + spectrum.g, self.b + spectrum.b)

    def __sub__(self, spectrum):
        return RGBSpectrum(self.r - spectrum.r, self.g - spectrum.g, self.b - spectrum.b)

    def __mul__(self, t):
        if isinstance(t, RGBSpectrum):
            return self.mix_spectrum(t)
        return RGBSpectrum(self.r * t, self.g * t, self.b * t)

    def __rmul__(self, t):
        if isinstance(t, RGBSpectrum):
            return self.mix_spectrum(t)
        return RGBSpectrum(self.r * t, self.g * t, self.b * t)

    def mix_spectrum(self, spectrum):
        return RGBSpectrum(self.r * spectrum.r, self.g * spectrum.g, self.b * spectrum.b)

    #TODO -- zero division
    def divide_spectrum(self, spectrum):
        return RGBSpectrum(self.r / spectrum.r, self.g / spectrum.g, self.b / spectrum.b)

    def scale(self, t):
        self.r = t * self.r
        self.g = t * self.g
        self.b = t * self.b
        return self

    def to_ds(self):
        return (float(self.r), float(self.g), float(self.b), 0.0)

    def clamp(self, low=0.0, high=100000000.0):
        if self.r > high: self.r = high 
        if self.g > high: self.g = high 
        if self.b > high: self.b = high 
        if self.r < low: self.r = low 
        if self.g < low: self.g = low 
        if self.b < low: self.b = low 

    def black(self):
        return RGBSpectrum(0.0, 0.0, 0.0)

    def set(self, value):
        value = float(value)
        self.r = value
        self.g = value
        self.b = value
        return self

    def asm_struct(self):
        code = """
        struct Spectrum
        float values[4]
        end struct
        """
        return code

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
            return self.mix_spectrum(t)
        samples = [self.samples[i] * t for i in range(len(self.samples))]
        return SampledSpectrum(samples)

    def __rmul__(self, t):
        if isinstance(t, SampledSpectrum):
            return self.mix_spectrum(t)
        samples = [self.samples[i] * t for i in range(len(self.samples))]
        return SampledSpectrum(samples)

    def mix_spectrum(self, spectrum):
        samples = [self.samples[i] * spectrum.samples[i] for i in range(len(self.samples))]
        return SampledSpectrum(samples)

    #TODO -- zero division
    def divide_spectrum(self, spectrum):
        samples = [self.samples[i] / spectrum.samples[i] for i in range(len(self.samples))]
        return SampledSpectrum(samples)

    def scale(self, t):
        self.samples = [self.samples[i] * t for i in range(len(self.samples))]
        return self

    def to_ds(self):
        return tuple(self.samples)

    def clamp(self, low=0.0, high=100000000.0):
        for i in range(len(self.samples)):
            if self.samples[i] > high: self.samples[i] = high
            if self.samples[i] < low: self.samples[i] = low

    def black(self):
        vals = [0.0 for i in range(len(self.samples))] 
        return SampledSpectrum(vals)

    def set(self, value):
        value = float(value)
        self.samples = [value for i in range(len(self.samples))]
        return self

    def asm_struct(self):
        code = "struct Spectrum \n"
        code += "float values[ %i ] \n" % len(self.samples)
        code += "end struct \n"
        return code




import renmas.gui
import renmas


class Film:
    def __init__(self, width, height, nsamples=1):
        self.width = width
        self.height = height
        self.nsamples = nsamples

        self.image = renmas.gui.ImageFloatRGBA(width, height)

        self.spectrum = renmas.core.Spectrum(0.0, 0.0, 0.0)
        self.curn = nsamples

    def numsamples(self):
        return self.nsamples

    def set_resolution(width, height):
        self.width = width
        self.height = height
        #TODO - new image is needed FIXME
        
    def set_nsamples(self, n):
        self.nsamples = n
        self.curn = n

    def add_sample(self, sample, hitpoint):
        if self.curn == 1:
            self.spectrum = self.spectrum + hitpoint.spectrum
            self.spectrum.scale(1.0/self.nsamples)
            spec = self.spectrum

            #spec.clamp() FIXME make clamp to certen color so to know when picture is wrong 
            iy = self.height - sample.iy #flip the image
            self.image.set_pixel(sample.ix, iy, spec.r, spec.g, spec.b)
            self.curn = self.nsamples
            self.spectrum = renmas.core.Spectrum(0.0, 0.0, 0.0)
        else:
            self.spectrum = self.spectrum + hitpoint.spectrum
            self.curn -= 1


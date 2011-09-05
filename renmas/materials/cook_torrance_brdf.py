
import renmas
import math
import renmas.utils as util

class GaussianDistribution:
    def __init__(self, c, m):
        self.c = float(c)
        self.m = float(m)

    def D(self, hitpoint, h):
        ndoth = hitpoint.normal.dot(h)
        alpha = math.acos(ndoth)
        g = alpha / self.m
        d = self.c * math.exp(-g*g)
        return d

    def D_asm(self, runtime):
        util.load_func(runtime, "fast_acos_ss", "fast_exp_ss")

        #eax pointer to hitpoint
        #ebx pointer to H (half vector)
        name = "DistGauss" + str(hash(self))
        ASM = """
        #DATA
        """
        ASM += "float " + name + "m \n" 
        ASM += "float " + name + "c \n" 
        ASM += "float " + name + "minus_one = -1.0 \n" 
        ASM += "#CODE \n"
        ASM += "macro dot xmm0 = eax.hitpoint.normal * ebx \n"
        ASM += "call fast_acos_ss \n"
        ASM += "macro eq32 xmm0 = xmm0 / " + name + "m \n"
        ASM += "macro eq32 xmm0 = xmm0 * xmm0 \n"
        ASM += "macro eq32 xmm0 = xmm0 * " + name + "minus_one \n"
        ASM += "call fast_exp_ss \n"
        ASM += "macro eq32 xmm0 = xmm0 * " + name + "c \n"

        return ASM

    def populate_ds(self, ds):
        name = "DistGauss" + str(hash(self)) + "m"
        ds[name] = self.m 
        name = "DistGauss" + str(hash(self)) + "c"
        ds[name] = self.c 

class BeckmannDistribution:
    def __init__(self, m):
        self.m = float(m)

    def D(self, hitpoint, h):
        ndoth = hitpoint.normal.dot(h)
        alpha = math.acos(ndoth)
        tana = math.tan(alpha) / self.m
        cosa = math.cos(alpha)
        cosa *= cosa
        return math.exp(-tana*tana) / (self.m * self.m * cosa * cosa) 

    def D1(self, hitpoint, h):
        
        ndoth = hitpoint.normal.dot(h)
        if ndoth < 0.00001: return 0.0
        return (self.m+2.0) * math.pow(ndoth, self.m) / (2.0*math.pi)


    def D_asm(self, runtime):

        util.load_func(runtime, "fast_acos_ss", "fast_cos_ss", "fast_tan_ss", "fast_exp_ss")
        #eax pointer to hitpoint
        #ebx pointer to H (half vector)
        name = "DistBeck" + str(hash(self))
        ASM = """
        #DATA
        """
        ASM += "float " + name + "m \n" 
        ASM += "float " + name + "minus_one = -1.0 \n" 
        ASM += "float " + name + "alpha \n"
        ASM += "float " + name + "temp \n"
        ASM += "#CODE \n"
        ASM += "macro dot xmm0 = eax.hitpoint.normal * ebx \n"
        ASM += "call fast_acos_ss \n"
        ASM += "macro eq32 " + name + "alpha = xmm0 \n"
        ASM += "call fast_tan_ss \n"
        ASM += "macro eq32 xmm0 = xmm0 / " + name + "m \n"
        ASM += "macro eq32 xmm0 = xmm0 * xmm0 \n"
        ASM += "macro eq32 xmm0 = xmm0 * " + name + "minus_one \n"
        ASM += "call fast_exp_ss \n"
        ASM += "macro eq32 " + name + "temp = xmm0 \n"
        ASM += "macro eq32 xmm0 = " + name + "alpha \n"
        ASM += "call fast_cos_ss \n"
        ASM += "macro eq32 xmm0 = xmm0 * xmm0 \n"
        ASM += "macro eq32 xmm1 = xmm0 * xmm0 \n"
        ASM += "macro eq32 xmm1 = xmm1 * " + name + "m \n"
        ASM += "macro eq32 xmm1 = xmm1 * " + name + "m \n"
        ASM += "macro eq32 xmm0 = " + name + "temp \n"
        ASM += "macro eq32 xmm0 = xmm0 / xmm1 \n"

        return ASM

    def populate_ds(self, ds):
        name = "DistBeck" + str(hash(self)) + "m"
        ds[name] = self.m 

class CookTorranceBRDF:
    def __init__(self, spectrum, distribution, k=None):
        self.k = k
        self.spectrum = spectrum
        self.one = renmas.core.Spectrum(1.0, 1.0, 1.0)
        self.dist = distribution
        self.k = 0.02

    def brdf(self, hitpoint):
        #geometric term G
        h = (hitpoint.wo + hitpoint.wi).normalize()
        ndoth = hitpoint.normal.dot(h)
        ndotv = hitpoint.normal.dot(hitpoint.wo)
        vdoth = hitpoint.wo.dot(h)
        ndotl = hitpoint.normal.dot(hitpoint.wi)

        G = min(1.0, 2.0*ndoth*ndotv/vdoth, 2.0*ndoth*ndotl/vdoth)
        D = self.dist.D(hitpoint, h)
        #Schlick approx.
        tmp = 1.0 - ndotl
        tmp2 = tmp * tmp * tmp * tmp * tmp
        F = self.spectrum + (self.one - self.spectrum)*tmp2 
        
        spec = F * D * G * (1/(math.pi * ndotl * ndotv))
        if self.k is None:
            return spec
        else:
            return spec * self.k


    def brdf_asm(self, runtime):
        
        #eax pointer to hitpoint
        name = "CookTorr" + str(hash(self))

        ASM = """
        #DATA
        """
        ASM += "float " + name + "spectrum[4] \n" 
        ASM += "float " + name + "k[4] \n"
        ASM += "float " + name + "h[4] \n"
        ASM += "uint32 " + name + "hp_ptr \n"
        ASM += "float " + name + "one[4] = 1.0, 1.0, 1.0, 0.0 \n" 
        ASM += "float " + name + "two = 2.0 \n"
        ASM += "float " + name + "D \n"
        ASM += "float " + name + "G \n"
        ASM += "float " + name + "pi = 3.141592653589 \n"
        ASM += "#CODE \n"
        ASM += "mov dword [" + name + "hp_ptr], eax \n"
        ASM += "macro eq128 xmm0 = eax.hitpoint.wo + eax.hitpoint.wi \n"
        ASM += util.normalization("xmm0", "xmm1", "xmm2")
        ASM += "macro eq128 " + name + "h = xmm0 \n"
        ASM += "mov ebx, " + name + "h \n"
        ASM += self.dist.D_asm(runtime)
        ASM += "macro eq32 " + name + "D = xmm0 \n"
        ASM += "mov eax, dword [" + name + "hp_ptr]\n"
        ASM += "macro dot xmm0 = eax.hitpoint.normal * " + name + "h \n"
        ASM += "macro dot xmm1 = eax.hitpoint.normal * eax.hitpoint.wo {xmm0} \n"
        ASM += "macro dot xmm2 = eax.hitpoint.wo * " + name + "h {xmm0, xmm1} \n"
        ASM += "macro dot xmm3 = eax.hitpoint.normal *  eax.hitpoint.wi {xmm0, xmm1, xmm2} \n"
        ASM += "macro eq32 xmm4 = " + name + "one \n"
        ASM += "macro eq32 xmm4 = xmm4 / xmm2 \n"
        ASM += "macro eq32 xmm5 = " + name + "two \n"
        ASM += "macro eq32 xmm5 = xmm5 * xmm0 \n"
        ASM += "macro eq32 xmm6 = xmm5 \n"
        ASM += "macro eq32 xmm6 = xmm6 * xmm1 \n"
        ASM += "macro eq32 xmm5 = xmm5 * xmm3 \n"
        ASM += "macro eq32 xmm6 = xmm6 * xmm4 \n"
        ASM += "macro eq32 xmm5 = xmm5 * xmm4 \n"
        ASM += "minss xmm6, dword [" + name + "one] \n"
        ASM += "minss xmm6, xmm5 \n"
        ASM += "macro eq32 " + name + "G = xmm6 \n"
        ASM += "macro eq32 xmm4 = " + name + "one \n" 
        ASM += "macro eq32 xmm4 = xmm4 - xmm3 \n"
        ASM += "macro eq32 xmm5 = xmm4 \n"
        ASM += "macro eq32 xmm5 = xmm5 * xmm5 \n"
        ASM += "macro eq32 xmm5 = xmm5 * xmm5 \n"
        ASM += "macro eq32 xmm5 = xmm5 * xmm4 \n"
        ASM += "macro broadcast xmm5 = xmm5[0] \n"
        ASM += "macro eq128 xmm6 = " + name + "one \n"
        ASM += "macro eq128 xmm6 = xmm6 - " + name + "spectrum \n"
        ASM += "macro eq128 xmm6 = xmm6 * xmm5 \n"
        #F is in xmm6
        ASM += "macro eq128 xmm6 = xmm6 + " + name + "spectrum \n"
        ASM += "macro eq32 xmm3 = xmm3 * xmm1 \n"
        ASM += "macro eq32 xmm3 = xmm3 * " + name + "pi \n"
        ASM += "macro eq32 xmm7 = " + name + "D \n"
        ASM += "macro eq32 xmm7 = xmm7 * " + name + "G \n"
        ASM += "macro eq32 xmm7 = xmm7 / xmm3 \n"
        ASM += "macro broadcast xmm0 = xmm7[0] \n"
        ASM += "macro eq128 xmm0 = xmm0 * xmm6 \n"

        if self.k is not None:
            ASM += "macro eq128 xmm0 = xmm0 * " + name + "k\n"

        return ASM

    def populate_ds(self, ds):
        s = self.spectrum
        name = "CookTorr" + str(hash(self)) + "spectrum"
        ds[name] = (s.r, s.g, s.b, 0.0)
        if self.k is not None:
            name = "CookTorr" + str(hash(self)) + "k"
            ds[name] = (self.k, self.k, self.k, 0.0)

        self.dist.populate_ds(ds)


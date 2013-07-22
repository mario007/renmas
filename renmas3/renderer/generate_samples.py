import math
from random import random
from itertools import accumulate
from renmas3.base import Vector3

class Distribution1D:
    def __init__(self, pdfs, cdfs, max_cdf):
        self.pdfs = pdfs
        self.cdfs = cdfs
        self.max_cdf = max_cdf

def create_1d_distribution(values):
    sum_pdf = sum(values)
    if sum_pdf <= 0.0:
        pdf = [0.0] * len(values)
        sum_pdf = 1.0
    else:
        pdf = list(values)
    
    cdf = list(accumulate(pdf))
    max_cdf = max(cdf)
    if max_cdf > 0.0:
        for i in range(len(cdf)):
            cdf[i] =  cdf[i] / max_cdf

    for i in range(len(pdf)):
        pdf[i] = pdf[i] / sum_pdf

    return Distribution1D(pdf, cdf, max_cdf)

def sampling_1d_distribution(distr, u):
    arr = [abs(n - u) for n in distr.cdfs]
    val = min(arr)
    index = arr.index(val)
    return index, val

def get_lums(img, y):
    lums = []
    for i in range(img.width):
        p = img.get_pixel(i, y)
        l = 0.213 * p[0] + 0.715 * p[1] + 0.072 * p[2]
        lums.append(l)
    return lums

def pol_vec(theta, phi):
    sin_theta = math.sin(theta)
    x = math.cos(phi) * sin_theta
    y = math.cos(theta) 
    z = math.sin(phi) * sin_theta
    return Vector3(x, y, z)

class EnvSample():
    def __init__(self, vec, pdf):
        self.vec = vec
        self.pdf = pdf

def generate_samples(img, nsamples):
    
    # Creation of 1D distributions for sampling
    c_distr = []
    values = [0.0] * img.height
    for i in range(img.height):
        # 1D Distribution
        lums = get_lums(img, i)
        tmp_distr = create_1d_distribution(lums)
        c_distr.append(tmp_distr)
        values[i] = tmp_distr.max_cdf
    r_distr = create_1d_distribution(values)
    

    # Sampling
    samples = []
    pi22 = 2 * math.pi * 2 * math.pi
    for i in range(nsamples):
        u1 = random()
        u2 = random()

        val1, pdf1 = sampling_1d_distribution(r_distr, u1)

        val2, pdf2 = sampling_1d_distribution(c_distr[val1], u2) 

        phi = math.pi * 2.0 * val1 / img.height
        theta = math.pi * val2 / img.width
        
        vec = pol_vec(theta, phi)
        pdf = (pdf1 * pdf2) / (pi22 * abs(math.sin(theta)))
        img.set_pixel(val2, val1, 0.0, 0.99, 0.0)
        samples.append(EnvSample(vec, pdf))

    return samples


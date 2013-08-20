import math
from random import random
from itertools import accumulate
from renmas3.base import Vector3, ImagePRGBA

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

def sampling_1d_distribution_binary(distr, u):
    #binary search implementation
    imin = 0
    new_arr = list(distr.cdfs)
    new_arr.append(1.0)
    imax = len(new_arr) - 2
    while imin <= imax:
        #midpoint
        mid = (imin + imax) // 2
        midval = new_arr[mid]
        midval2 = new_arr[mid+1]
        if u < midval:
            imax = mid - 1
        elif u > midval2:
            imin = mid + 1
        else:
            tv = (midval + midval2) / 2.0
            if u > tv:
                mid = mid + 1
                midval = new_arr[mid]
            break
    midval = abs(midval - u)
    return mid, midval

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

def _set_lat_long_coords(u, v):
    theta = u * math.pi
    phi = v * 2 * math.pi
    x = math.sin(theta) * math.cos(phi)
    y = math.cos(theta)
    z = -math.sin(theta) * math.sin(phi)
    return x, y, z

def _get_mirror_ball_pixel_coord(x, y, z):
    u = x / math.sqrt(2 * (1 + z))
    v = y / math.sqrt(2 * (1 + z))
    return u, v

def conv_angular_to_ll(img):
    width, height = img.size()
    new_img = ImagePRGBA(width*2, height)
    for j in range(height):
        for i in range(width * 2):
            x, y, z = _set_lat_long_coords(1 - j / float(height - 1), i / float(width * 2 - 1))
            u, v = _get_mirror_ball_pixel_coord(x, y, z)
            #convert to pixel coordiantes
            u = (u + 1) * 0.5 * width
            v = (v + 1) * 0.5 * height
            r, g, b, a = img.get_pixel(int(u), int(v))
            new_img.set_pixel(i, j, r, g, b, a)
    return new_img

def generate_samples(img, nsamples):
    img = conv_angular_to_ll(img)
    
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
    pi22 = 2 * math.pi * math.pi
    max_r = max_g = max_b = 0.0
    min_r = min_g = min_b = 0.0
    for i in range(nsamples):
        u1 = random()
        u2 = random()

        val1, pdf1 = sampling_1d_distribution(r_distr, u1)
        val1, pdf1 = sampling_1d_distribution_binary(r_distr, u1)

        val2, pdf2 = sampling_1d_distribution(c_distr[val1], u2) 
        val2, pdf2 = sampling_1d_distribution_binary(c_distr[val1], u2) 

        phi = math.pi * 2.0 * val1 / img.height
        theta = math.pi * val2 / img.width
        
        vec = pol_vec(theta, phi)
        if abs(math.sin(theta)) == 0.0:
            continue

        pdf = (pdf1 * pdf2) / (pi22 * abs(math.sin(theta)))

        r, g, b, a = img.get_pixel(val2, val1)
        tmp = float(img.width * img.height)
        max_r = max(max_r, r / pdf / tmp)
        max_g = max(max_g, g / pdf / tmp)
        max_b = max(max_b, b / pdf / tmp)
        min_r = min(min_r, r / pdf / tmp)
        min_g = min(min_g, g / pdf / tmp)
        min_b = min(min_b, b / pdf / tmp)

        img.set_pixel(val2, val1, 0.0, 0.99, 0.0)
        samples.append(EnvSample(vec, pdf))
    
    print(max_r, max_g, max_b)
    print(min_r, min_g, min_b)
    return samples



from itertools import accumulate
from math import sin, asin, pi, radians, cos, atan2, exp, tan, acos, atan2
from renmas3.base import Vector3, FloatArray, FloatArray2D
from .surface import SurfaceShader

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

def get_lums(img, y):
    lums = []
    for i in range(img.width):
        p = img.get_pixel(i, y)
        l = 0.213 * p[0] + 0.715 * p[1] + 0.072 * p[2]
        lums.append(l)
    return lums

class EnvLight:
    def __init__(self, image, col_mgr):
        self._image = image
        self._col_mgr = col_mgr
        self._prepare_light(image)

    def _prepare_light(self, img):
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

        #prepare structure for shader
        arr = FloatArray()
        for v in r_distr.cdfs:
            arr.append(v)
        arr.append(1.0)
        self._arr1 = arr

        arr2d = FloatArray2D(img.width + 1, img.height)
        for y in range(img.height):
            d = c_distr[y]
            for x in range(img.width):
                arr2d[x, y] = d.cdfs[x]
            arr2d[x, y] = 1.0
        self._arr2 = arr2d


    def prepare_illuminate(self, runtimes):

        code = """
u = random2()
u1 = u[0]
u2 = u[1]
pi22 = 19.7392 # 2 * math.pi * math.pi

#binary search
imin = 0
imax = _imax_raw
while imin <= imax:
    mid = (imin + imax) / 2
    midval = get_item(arr1, mid)
    mid2 = mid + 1
    midval2 = get_item(arr1, mid2)
    if u1 < midval:
        imax = mid - 1
    else:
        tmp = 0 # else if problem!!! its not suported
        if u1 > midval2:
            imin = mid + 1
        else:
            tv = (midval + midval2) * 0.5
            if u1 > tv:
                mid = mid + 1
                midval = get_item(arr1, mid)
            break
midval = midval - u1
if midval < 0.0:
    midval = midval * -1.0

val1 = mid
pdf1 = midval

#binary search
imin = 0
imax = _imax_col
while imin <= imax:
    mid = (imin + imax) / 2
    midval = get_item(arr2, mid, val1)
    mid2 = mid + 1
    midval2 = get_item(arr2, mid2, val1)
    if u2 < midval:
        imax = mid - 1
    else:
        tmp = 0 # else if problem its not usported
        if u2 > midval2:
            imin = mid + 1
        else:
            tv = (midval + midval2) * 0.5
            if u2 > tv:
                mid = mid + 1
                midval = get_item(arr2, mid, val1)
            break
midval = midval - u2
if midval < 0.0:
    midval = midval * -1.0

val2 = mid
pdf2 = midval

height = float(img.height)
width = float(img.width)


#phi = 6.2831853 * val1 / height
#theta = 3.14159 * val2 / width
u = float(val2) / width * 2.0
v = float(val1) / height
theta = 3.14159 * (u - 1.0)
phi = 3.14159 * v

tmp = sin(theta)
if tmp < 0.0:
    tmp = tmp * -1.0
tmp = tmp * pi22
pdf = pdf1 * pdf2 / tmp

x = sin(phi) * sin(theta)
y = cos(phi)
z = sin(phi) * cos(theta)
z = z * -1.0
#sin_theta = sin(theta)
#x = cos(phi) * sin_theta
#y = cos(theta)
#z = sin(phi) * sin_theta

wi = float3(x, y, z)
wi = normalize(wi)

large_value = 1000.0
shadepoint.wi = wi
shadepoint.light_position = wi * large_value
rgba = get_rgba(img, val2, val1)
spec = rgb_to_spectrum(rgba)

tmp = img.width * img.height
pdf = pdf * float(tmp)
inv_pdf = 1.0 / pdf
scale = 0.00001 
spec = spec * inv_pdf * scale
shadepoint.light_intensity = spec
        """

        imax_raw = len(self._arr1) - 2
        imax_col = len(self._arr1) - 2

        props = {
                'arr1': self._arr1, '_imax_raw': imax_raw,
                '_imax_col': imax_col, 'arr2': self._arr2,
                'img': self._image
                }
        shader = SurfaceShader(code, props=props, col_mgr=self._col_mgr)
        shader.prepare(runtimes, [])
        name = shader.method_name()
        ptrs = [r.address_label(name) for r in runtimes]
        return ptrs

    def prepare_environment(self, name, runtimes):
        code = """
d = shadepoint.wo
phi = acos(d[1])
tmp = 1.0 / d[0]
theta = atanr2(d[2], tmp)
tmp = 0.5 * theta / 3.14159
u = 0.5 - tmp
v = phi / 3.14159

width = img.width - 1
height = img.height - 1
x = width * u 
y = height * v

x = int(x)
y = int(y)

if x > width:
    x = width

if y > height:
    y = height
rgba = get_rgba(img, x, y)
spec = rgb_to_spectrum(rgba)
shadepoint.light_intensity = spec

        """
        props = {
                'img': self._image
                }
        emission = SurfaceShader(code, props=props, col_mgr=self._col_mgr,
                method_name=name)
        emission.prepare(runtimes, [])
        return emission.shader

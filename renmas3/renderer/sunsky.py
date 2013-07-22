
from math import sin, asin, pi, radians, cos, atan2, exp, tan, acos, atan2
from renmas3.base import Vector3
from .surface import SurfaceShader

# latitude - (0 - 360)
# longitude - (-90, 90) south to north
# sm = standard meridian -- actually time zone number 
# jd = julian day (1 - 365)
# time_of_day (0.0 - 23.99) 14.25 = 2.15PM
# turbidity (1.0, 30+) 2-6 are most useful for clear day 

class SunSky:
    def __init__(self, col_mgr, latitude=20.0, longitude=0.0, sm=0, jd=80,
            time_of_day=7.0, turbidity=2.0):

        self._col_mgr = col_mgr
        self._latitude = latitude
        self._longitude = longitude
        self._sm = sm * 15.0 # sm is actually time zone number (east to west, zero based)
        self._jd = jd
        self._time_of_day = time_of_day
        self._turbidity = turbidity

        self._calc_sun_position()

        sun_solid_angle = 0.25 * pi * 1.39 * 1.39 / (150 * 150) # = 6.7443e-05

        T = self._turbidity
        self._perez_Y = [0.0] * 6
        self._perez_Y[1] =    0.17872 *T  - 1.46303
        self._perez_Y[2] =   -0.35540 *T  + 0.42749
        self._perez_Y[3] =   -0.02266 *T  + 5.32505
        self._perez_Y[4] =    0.12064 *T  - 2.57705
        self._perez_Y[5] =   -0.06696 *T  + 0.37027
      
        self._perez_x = [0.0] * 6
        self._perez_x[1] =   -0.01925 *T  - 0.25922
        self._perez_x[2] =   -0.06651 *T  + 0.00081
        self._perez_x[3] =   -0.00041 *T  + 0.21247
        self._perez_x[4] =   -0.06409 *T  - 0.89887
        self._perez_x[5] =   -0.00325 *T  + 0.04517
      
        self._perez_y = [0.0] * 6
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

    def get_sky_spectrum(self, direction):
        d = direction
        if d.y < 0.0: 
            return self._col_mgr.black()
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
        spec = self._col_mgr.chromacity_to_spectrum(x, y)
        spec = spec * (Y / self._col_mgr.Y(spec))
        return spec
        
    def prepare_illuminate(self, runtimes):
        code = """

d = sun_position - hitpoint.hit
d = normalize(d)
shadepoint.wi = d 
shadepoint.light_position = sun_position

if d[1] < 0.0:
    shadepoint.light_intensity = spectrum(0.0)
if d[1] < 0.001:
    d = float3(d[0], 0.001, d[2])
    d = normalize(d)

theta = acos(d[1])
tmp = 1.0 / d[2]
phi = atanr2(d[0], tmp)
if phi < 0.0:
    phi = 6.28318553 + phi

# angle bettwen this and sun
tmp = sin(theta) * sin(theta_sun)
tmp2 = phi_sun - phi
tmp = tmp * cos(tmp2)
cospsi = cos(theta) * cos(theta_sun) + tmp
gamma = acos(cospsi)
if cospsi > 1.0:
    gamma = 0.0
if cospsi < -1.0:
    gamma = 3.14159

#perez x calculation
tmp = exp(perez_x_2) * perez_x_1 + 1.0
tmp2 = perez_x_4 * theta_sun
tmp2 = exp(tmp2) * perez_x_3 + 1.0
tmp2 = cos(theta_sun) * cos(theta_sun) * perez_x_5 + tmp2
den = tmp * tmp2
tmp = perez_x_2 / cos(theta)
tmp = exp(tmp) * perez_x_1 + 1.0
tmp2 = perez_x_4 * gamma
tmp2 = exp(tmp2) * perez_x_3 + 1.0
tmp2 = cos(gamma) * cos(gamma) * perez_x_5 + tmp2
num = tmp * tmp2
x = zenith_x * num / den

#perez y calculation
tmp = exp(perez_y_2) * perez_y_1 + 1.0
tmp2 = perez_y_4 * theta_sun
tmp2 = exp(tmp2) * perez_y_3 + 1.0
tmp2 = cos(theta_sun) * cos(theta_sun) * perez_y_5 + tmp2
den = tmp * tmp2
tmp = perez_y_2 / cos(theta)
tmp = exp(tmp) * perez_y_1 + 1.0
tmp2 = perez_y_4 * gamma
tmp2 = exp(tmp2) * perez_y_3 + 1.0
tmp2 = cos(gamma) * cos(gamma) * perez_y_5 + tmp2
num = tmp * tmp2
y = zenith_y * num / den

#perez Y calculation
tmp = exp(perez_Y_2) * perez_Y_1 + 1.0
tmp2 = perez_Y_4 * theta_sun
tmp2 = exp(tmp2) * perez_Y_3 + 1.0
tmp2 = cos(theta_sun) * cos(theta_sun) * perez_Y_5 + tmp2
den = tmp * tmp2
tmp = perez_Y_2 / cos(theta)
tmp = exp(tmp) * perez_Y_1 + 1.0
tmp2 = perez_Y_4 * gamma
tmp2 = exp(tmp2) * perez_Y_3 + 1.0
tmp2 = cos(gamma) * cos(gamma) * perez_Y_5 + tmp2
num = tmp * tmp2
Y = zenith_Y * num / den

spec = chromacity_to_spectrum(x, y)
spec = Y / luminance(spec) * spec
scale = 0.005
spec = scale * spec
shadepoint.light_intensity = spec

        """

        position = 100 * self._dir_to_sun

        props = {'theta_sun': self._theta_sun, 'phi_sun': self._phi_sun,
                'zenith_x': self._zenith_x, 'perez_x_1': self._perez_x[1],
                'perez_x_2': self._perez_x[2], 'perez_x_3': self._perez_x[3],
                'perez_x_4': self._perez_x[4], 'perez_x_5': self._perez_x[5],
                'zenith_y': self._zenith_y, 'perez_y_1': self._perez_y[1],
                'perez_y_2': self._perez_y[2], 'perez_y_3': self._perez_y[3],
                'perez_y_4': self._perez_y[4], 'perez_y_5': self._perez_y[5],
                'zenith_Y': self._zenith_Y, 'perez_Y_1': self._perez_Y[1],
                'perez_Y_2': self._perez_Y[2], 'perez_Y_3': self._perez_Y[3],
                'perez_Y_4': self._perez_Y[4], 'perez_Y_5': self._perez_Y[5],
                'sun_position': position
                }
        shader = SurfaceShader(code, props=props, col_mgr=self._col_mgr)
        shader.prepare(runtimes, [])
        name = shader.method_name()
        ptrs = [r.address_label(name) for r in runtimes]
        return ptrs

    def prepare_environment(self, name, runtimes):
        code = """

d = shadepoint.wo

if d[1] < 0.0:
    shadepoint.light_intensity = spectrum(0.0)
if d[1] < 0.001:
    d = float3(d[0], 0.001, d[2])
    d = normalize(d)

theta = acos(d[1])
tmp = 1.0 / d[2]
phi = atanr2(d[0], tmp)
if phi < 0.0:
    phi = 6.28318553 + phi

# angle bettwen this and sun
tmp = sin(theta) * sin(theta_sun)
tmp2 = phi_sun - phi
tmp = tmp * cos(tmp2)
cospsi = cos(theta) * cos(theta_sun) + tmp
gamma = acos(cospsi)
if cospsi > 1.0:
    gamma = 0.0
if cospsi < -1.0:
    gamma = 3.14159

#perez x calculation
tmp = exp(perez_x_2) * perez_x_1 + 1.0
tmp2 = perez_x_4 * theta_sun
tmp2 = exp(tmp2) * perez_x_3 + 1.0
tmp2 = cos(theta_sun) * cos(theta_sun) * perez_x_5 + tmp2
den = tmp * tmp2
tmp = perez_x_2 / cos(theta)
tmp = exp(tmp) * perez_x_1 + 1.0
tmp2 = perez_x_4 * gamma
tmp2 = exp(tmp2) * perez_x_3 + 1.0
tmp2 = cos(gamma) * cos(gamma) * perez_x_5 + tmp2
num = tmp * tmp2
x = zenith_x * num / den

#perez y calculation
tmp = exp(perez_y_2) * perez_y_1 + 1.0
tmp2 = perez_y_4 * theta_sun
tmp2 = exp(tmp2) * perez_y_3 + 1.0
tmp2 = cos(theta_sun) * cos(theta_sun) * perez_y_5 + tmp2
den = tmp * tmp2
tmp = perez_y_2 / cos(theta)
tmp = exp(tmp) * perez_y_1 + 1.0
tmp2 = perez_y_4 * gamma
tmp2 = exp(tmp2) * perez_y_3 + 1.0
tmp2 = cos(gamma) * cos(gamma) * perez_y_5 + tmp2
num = tmp * tmp2
y = zenith_y * num / den

#perez Y calculation
tmp = exp(perez_Y_2) * perez_Y_1 + 1.0
tmp2 = perez_Y_4 * theta_sun
tmp2 = exp(tmp2) * perez_Y_3 + 1.0
tmp2 = cos(theta_sun) * cos(theta_sun) * perez_Y_5 + tmp2
den = tmp * tmp2
tmp = perez_Y_2 / cos(theta)
tmp = exp(tmp) * perez_Y_1 + 1.0
tmp2 = perez_Y_4 * gamma
tmp2 = exp(tmp2) * perez_Y_3 + 1.0
tmp2 = cos(gamma) * cos(gamma) * perez_Y_5 + tmp2
num = tmp * tmp2
Y = zenith_Y * num / den

spec = chromacity_to_spectrum(x, y)
spec = Y / luminance(spec) * spec
shadepoint.light_intensity = spec

        """

        props = {'theta_sun': self._theta_sun, 'phi_sun': self._phi_sun,
                'zenith_x': self._zenith_x, 'perez_x_1': self._perez_x[1],
                'perez_x_2': self._perez_x[2], 'perez_x_3': self._perez_x[3],
                'perez_x_4': self._perez_x[4], 'perez_x_5': self._perez_x[5],
                'zenith_y': self._zenith_y, 'perez_y_1': self._perez_y[1],
                'perez_y_2': self._perez_y[2], 'perez_y_3': self._perez_y[3],
                'perez_y_4': self._perez_y[4], 'perez_y_5': self._perez_y[5],
                'zenith_Y': self._zenith_Y, 'perez_Y_1': self._perez_Y[1],
                'perez_Y_2': self._perez_Y[2], 'perez_Y_3': self._perez_Y[3],
                'perez_Y_4': self._perez_Y[4], 'perez_Y_5': self._perez_Y[5],
                }
        emission = SurfaceShader(code, props=props, col_mgr=self._col_mgr,
                method_name=name)
        emission.prepare(runtimes, [])
        return emission.shader


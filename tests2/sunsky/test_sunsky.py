
import renmas2

ren = renmas2.Renderer()
sk = renmas2.lights.SunSky(renderer=ren, latitude=80.0, longitude=43.0, sm=0, jd=224, time_of_day=16.50, turbidity=3.0)

print(sk._theta_sun)
print(sk._phi_sun)
print(sk._dir_to_sun)

direction = renmas2.Vector3(3.2, 8.5, 1.8)
direction.normalize()
spec = sk.get_sky_spectrum(direction)
spec2 = sk.Le(direction)
print(spec)
print(spec2)


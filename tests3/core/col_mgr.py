import time
from renmas3.base import ColorManager

start = time.clock()
mgr = ColorManager()
end = time.clock()
print(end-start)
print(mgr.create_spectrum((0.2, 0.3, 0.4)))

print(mgr.wavelengths())
print(len(mgr.wavelengths()))
print(mgr.wavelength_intervals())
print(len(mgr.wavelength_intervals()))


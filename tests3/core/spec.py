
from renmas3.core import Spectrum

s1 = Spectrum(False, (1.0, 1.0, 1.0))

s2 = Spectrum(False, (0.2, 0.2, 0.1))

print(s1*s2)


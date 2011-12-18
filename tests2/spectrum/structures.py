
from tdasm import Tdasm, Runtime
import renmas2
import renmas2.core


renderer = renmas2.Renderer()

print (renderer.spectrum_rendering)
print (renderer.spectrum_region)
s = renderer.structures
renderer.spectrum_rendering = True

renderer.spectrum_parameters(18, 320, 790)

print (renderer.spectrum_rendering)
print (renderer.spectrum_region)
print (renderer.nspectrum_samples)

print(s.structs(('spectrum','ray')))


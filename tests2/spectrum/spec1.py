import random
from tdasm import Tdasm, Runtime
import renmas2
import renmas2.core

#factory = renmas2.core.Factory()

#s = [(306, 1.2), (310, 2.2), (320, 3.4), (350, 2.8), (380, 2.4)]
#factory.create_spectrum(6, s, 290, 410)

renderer = renmas2.Renderer()
renderer.spectrum_rendering = True
structs = renderer.structures.get_struct('spectrum')


ASM = """
    #DATA
"""
ASM += structs +  """
    spectrum sp1
    spectrum sp2
    spectrum sp3
    struct hitpoint 
    spectrum d1
    end struct

    hitpoint sp4
    float re[8]
    float x = 0.5
    float suma
    #CODE
    ;mov ebx, sp1
    mov ecx, sp2
    mov eax, sp3
    mov edx, sp4
    macro eq32 xmm0 = x
    lea ebx, dword [edx + hitpoint.d1]
    macro spectrum eax = ebx * ecx
    ;macro spectrum eax = ecx
    ;macro spectrum eax = xmm0 * ecx
    ;macro spectrum sum ebx
    ;macro eq32 suma = xmm0 {xmm0}

    #END
"""

#print(ASM)
mc = renderer.assembler.assemble(ASM) 
mc.print_machine_code()

runtime = Runtime()
ds = runtime.load("test", mc)

if renderer.spectrum_rendering:
    arr1 = tuple([random.random() for i in range(renderer.nspectrum_samples)])
    arr2 = tuple([random.random() for i in range(renderer.nspectrum_samples)])
    sp1 = renmas2.core.Spectrum(True, arr1)
    sp2 = renmas2.core.Spectrum(True, arr2)
else:
    arr1 = tuple([random.random() for i in range(3)])
    arr2 = tuple([random.random() for i in range(3)])
    sp1 = renmas2.core.Spectrum(False, arr1)
    sp2 = renmas2.core.Spectrum(False, arr2)
#ds["sp1.values"] = sp1.to_ds()
ds["sp2.values"] = sp2.to_ds()
ds["sp4.d1.values"] = sp1.to_ds()

print(sp1)
print(sp2)
#print(sp1 + sp2)
#print(sp1 - sp2)
#print(0.2 * sp1)
#print(sp1.mix_spectrum(sp2))
#print(sp1.scale(0.10))
#print(sp1.to_ds())

runtime.run("test")

#print(arr1)
#print("Sum of arr1 array ", sum(arr1), ", ", ds["suma"])
#print(sp1)
#print(sp2)
print(ds["sp3.values"]) 
#print(ds["re"])



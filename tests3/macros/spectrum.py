import random
from tdasm import Tdasm, Runtime
from renmas3.core import ColorManager

def test_sum():
    mgr = ColorManager()
    ASM = "\n #DATA \n " + mgr.spectrum_struct() + """
    spectrum sp1
    float sum
    #CODE
    macro mov ebx, sp1
    macro spectrum sum ebx
    macro eq32 sum = xmm0 {xmm7}
    #END
    """
    mc = mgr.assembler.assemble(ASM) 
    #mc.print_machine_code()
    runtime = Runtime()
    ds = runtime.load("test", mc)
    col = mgr.create_spectrum((0.3, 0.2, 0.4))
    ds['sp1.values'] = col.to_ds() 
    runtime.run('test')
    print(ds['sum'])
    if col.sampled:
        print(sum(col.samples))
    else:
        print(col.r + col.g + col.b)

def test_clamp():
    mgr = ColorManager()
    ASM = "\n #DATA \n " + mgr.spectrum_struct() + """
    spectrum sp1
    float low =0.25
    float high = 0.35

    #CODE
    macro mov ebx, sp1
    macro eq32 xmm0 = low
    macro eq32 xmm1 = high
    macro spectrum clamp ebx
    #END
    """
    mc = mgr.assembler.assemble(ASM) 
    #mc.print_machine_code()
    runtime = Runtime()
    ds = runtime.load("test", mc)
    col = mgr.create_spectrum((0.3, 0.2, 0.4))
    ds['sp1.values'] = col.to_ds() 
    runtime.run('test')
    print(ds['sp1.values'])
    col.clamp(low=0.25, high=0.35)
    if col.sampled:
        print(col)
    else:
        print(col.r, col.g, col.b)
    pass

def test_scaling():
    mgr = ColorManager()
    ASM = "\n #DATA \n " + mgr.spectrum_struct() + """
    spectrum sp1, sp2
    float scale = 0.3

    #CODE
    macro mov ebx, sp1
    macro mov ecx, sp2
    macro eq32 xmm0 = scale
    macro spectrum ecx = xmm0 * ebx 
    #END
    """
    mc = mgr.assembler.assemble(ASM) 
    #mc.print_machine_code()
    runtime = Runtime()
    ds = runtime.load("test", mc)
    col = mgr.create_spectrum((0.3, 0.2, 0.4))
    ds['sp1.values'] = col.to_ds() 
    runtime.run('test')
    print(ds['sp2.values'])
    print(col*0.3)

def test_arithmetic():
    mgr = ColorManager()
    ASM = "\n #DATA \n " + mgr.spectrum_struct() + """
    spectrum sp1, sp2, sp3

    #CODE
    macro mov ebx, sp1
    macro mov eax, sp2
    macro mov ecx, sp3
    macro spectrum ecx = eax + ebx
    #END
    """
    mc = mgr.assembler.assemble(ASM) 
    #mc.print_machine_code()
    runtime = Runtime()
    ds = runtime.load("test", mc)
    col1 = mgr.create_spectrum((0.3, 0.2, 0.4))
    col2 = mgr.create_spectrum((0.1, 0.5, 0.1))
    ds['sp1.values'] = col1.to_ds() 
    ds['sp2.values'] = col2.to_ds() 
    runtime.run('test')
    print(ds['sp3.values'])
    print(col1+col2)
    pass

def test_set():
    mgr = ColorManager()
    ASM = "\n #DATA \n " + mgr.spectrum_struct() + """
    spectrum sp1
    float value = 0.3

    #CODE
    macro mov ebx, sp1
    macro eq32 xmm0 = value 
    macro spectrum ebx = xmm0
    #END
    """
    mc = mgr.assembler.assemble(ASM) 
    #mc.print_machine_code()
    runtime = Runtime()
    ds = runtime.load("test", mc)
    col = mgr.create_spectrum((0.3, 0.2, 0.4))
    ds['sp1.values'] = col.to_ds() 
    runtime.run('test')
    print(ds['sp1.values'])
    print(col.set(0.3))

#test_sum()
#test_clamp()
#test_scaling()
#test_arithmetic()
test_set()

ASM = """
    #DATA
"""
ASM += "structs" +  """
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
    float low =0.5
    float high = 0.6

    #CODE
    mov ebx, sp1
    macro eq32 xmm0 = low
    macro eq32 xmm1 = high
    macro spectrum clamp ebx
    ;macro spectrum ebx = xmm0

    ;mov ecx, sp2
    ;mov eax, sp3
    ;mov edx, sp4
    ;macro eq32 xmm0 = x
    ;lea ebx, dword [edx + hitpoint.d1]
    ;macro spectrum eax = ebx * ecx
    ;macro spectrum eax = ecx
    ;macro spectrum eax = xmm0 * ecx
    ;macro spectrum sum ebx
    ;macro eq32 suma = xmm0 {xmm0}
    ;mov eax, sp3
    ;macro eq32 xmm3 = x
    ;macro call zero xmm3
    ;macro spectrum eax = xmm3

    #END
"""

#print(ASM)
#mc = renderer.assembler.assemble(ASM) 
#mc.print_machine_code()

#runtime = Runtime()
#ds = runtime.load("test", mc)

#if renderer.spectral_rendering:
#    arr1 = tuple([random.random() for i in range(renderer.nspectrum_samples)])
#    arr2 = tuple([random.random() for i in range(renderer.nspectrum_samples)])
#    sp1 = renmas2.core.Spectrum(True, arr1)
#    sp2 = renmas2.core.Spectrum(True, arr2)
#else:
#    arr1 = tuple([random.random() for i in range(3)])
#    arr2 = tuple([random.random() for i in range(3)])
#    sp1 = renmas2.core.Spectrum(False, arr1)
#    sp2 = renmas2.core.Spectrum(False, arr2)
#ds["sp1.values"] = sp1.to_ds()
#ds["sp2.values"] = sp2.to_ds()
#ds["sp4.d1.values"] = sp1.to_ds()

#print(sp1)
#print(sp2)
#print(sp1 + sp2)
#print(sp1 - sp2)
#print(0.2 * sp1)
#print(sp1.mix_spectrum(sp2))
#print(sp1.scale(0.10))
#print(sp1.to_ds())

#print(sp1)
#runtime.run("test")
#print(ds["sp1.values"])

#print(arr1)
#print("Sum of arr1 array ", sum(arr1), ", ", ds["suma"])
#print(sp1)
#print(sp2)
#print(ds["sp3.values"]) 
#print(ds["re"])



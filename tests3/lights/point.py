
import platform
from tdasm import Runtime
from renmas3.core import Factory, ColorManager
from renmas3.core.structures import SHADEPOINT
from renmas3.loaders import load_spd

mgr = ColorManager(False)
factory = Factory()

light = factory.create_light(mgr=mgr, typ='point', source='A',\
        position=(9,10,9), direction=(2,2,2))


hp = factory.shade_point()

s = light.L(hp)
print(hp.wi)
print(hp.light_position)
print(hp.light_spectrum)

runtime = Runtime()
light.L_asm([runtime], mgr.assembler, mgr.spectrum_struct())

structs = mgr.spectrum_struct() + SHADEPOINT
bits = platform.architecture()[0]
if bits == '64bit':
    ASM = "#DATA \n" + structs + """
        shadepoint sp1
        uint64 ptr_light
        #CODE
        macro mov eax, sp1
        call qword [ptr_light] 
        #END
    """
else:
    ASM = "#DATA \n" + structs + """
        shadepoint sp1
        uint32 ptr_light
        #CODE
        macro mov eax, sp1
        call dword [ptr_light] 
        #END
    """

mc = mgr.assembler.assemble(ASM)
#mc.print_machine_code()
ds = runtime.load('test', mc)
ds['ptr_light'] = runtime.address_module(light.light_asm_name)
ds['sp1.hit'] = hp.hit.to_ds()

runtime.run('test')
print('--------------------------')
print(ds['sp1.wi'])
print(ds['sp1.light_position'])
print(ds['sp1.light_spectrum.values'])


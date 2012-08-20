
from tdasm import Runtime
from renmas3.core import Factory, ColorManager, ShadePoint
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
light.L_asm([runtime], mgr.assembler)

structs = mgr.spectrum_struct() + ShadePoint.struct() 
ASM = "#DATA \n" + structs + """
    shadepoint sp1
    #CODE
    macro mov eax, sp1
"""
ASM += 'call ' + light.L_asm_label + """
    #END
"""
mc = mgr.assembler.assemble(ASM)
#mc.print_machine_code()
ds = runtime.load('test', mc)
ds['sp1.hit'] = hp.hit.to_ds()

runtime.run('test')
print('--------------------------')
print(ds['sp1.wi'])
print(ds['sp1.light_position'])
print(ds['sp1.light_spectrum.values'])


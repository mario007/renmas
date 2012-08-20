
import platform
from tdasm import Runtime
from renmas3.core import ColorManager, ShadePoint, Material, Factory
from renmas3.materials import Lambertian

col_mgr = ColorManager(False)

mat = Material(col_mgr.zero_spectrum())

lamb = Lambertian(col_mgr.create_spectrum((0.3,0.4,0.6)))

mat.add(lamb)

factory = Factory()
sp = factory.shade_point()
sp.normal = factory.vector3(0,1,0)
sp.wi = factory.vector3(2,2,2)

print(mat.brdf(sp))

runtime = Runtime()
mat.brdf_asm([runtime], col_mgr.assembler)

bits = platform.architecture()[0]
if bits == '64bit':
    ASM = "#DATA \n" + col_mgr.zero_spectrum().struct() + ShadePoint.struct() + """
        shadepoint sp1
        uint64 ptr_brdf
        #CODE
        macro mov eax, sp1
        call qword [ptr_brdf] 
        #END
    """
else:
    ASM = "#DATA \n" + col_mgr.zero_spectrum().struct() + ShadePoint.struct() + """
        shadepoint sp1
        uint32 ptr_brdf
        #CODE
        macro mov eax, sp1
        call dword [ptr_brdf] 
        #END
    """

mc = col_mgr.assembler.assemble(ASM)
#mc.print_machine_code()
ds = runtime.load('test', mc)
ds['ptr_brdf'] = runtime.address_module(mat.brdf_asm_name)
ds['sp1.normal'] = sp.normal.to_ds()
ds['sp1.wi'] = sp.wi.to_ds()

runtime.run('test')

print(ds['sp1.f_spectrum.values'])


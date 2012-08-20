
import time
from tdasm import Runtime

import renmas3
import renmas3.core
from renmas3.core import DirectLighting, Factory, ShadePoint
from renmas3.win32 import show_image_in_window

start = time.clock()
ren = renmas3.core.Renderer()
irender = renmas3.core.IRender(ren)
end = time.clock()
print(end-start)

filename = 'I:\\GitRENMAS\\tests3\\renderer\\sphere1.py'
filename = 'E:\\GitRENMAS\\renmas\\tests3\\renderer\\sphere1.py'

exec(compile(open(filename).read(), filename, 'exec'), dict(locals()), dict(globals()))

factory = Factory()
light = factory.create_light(mgr=ren.color_mgr, typ='point', source='A',\
        position=(9,10,9), direction=(2,2,2))

ren.add('point_light1', light)
ren.prepare()

direct_lighting = DirectLighting(ren)
sp = factory.shade_point(hit=(5,5,5))
sp.material = 0

ret = direct_lighting.estimate_direct(sp)
runtime = Runtime()
direct_lighting.estimate_direct_asm([runtime], 'estimate_dir')
print(ret)

structs = ren.color_mgr.zero_spectrum().struct() + ShadePoint.struct()
ASM = "#DATA \n" + structs + """
 #DATA
   spectrum spec1
  shadepoint sp1

 #CODE
 macro mov eax, sp1
 call estimate_dir
 macro mov ebx, spec1
 macro spectrum ebx = eax
 #END
"""

mc = ren.assembler.assemble(ASM)
ds = runtime.load('test', mc)
ds['sp1.hit'] = sp.hit.to_ds()
ds['sp1.material'] = sp.material
ds['sp1.normal'] = sp.normal.to_ds()

runtime.run('test')
print(ds['spec1.values'])


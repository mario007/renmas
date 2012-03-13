
import time
from renmas2.core import Obj 

obj = Obj()

#ret = obj.load("I:/Obj_files/box.obj")
start = time.clock()
#ret = obj.load("I:/Obj_files/cube.obj")
ret = obj.load("I:/Obj_files/mini_obj.obj")
#ret = obj.load("I:/Obj_files/luxball5.obj")
#ret = obj.load("I:/Obj_files/01_obj.obj")
end = time.clock()
print(end-start)

meshes = obj.meshes
nvertices = 0
ntriangles = 0
for m in meshes:
    print (type(m.vb), m.vb.size())
    print (type(m.tb), m.tb.size())
    nvertices += m.vb.size()
    ntriangles += m.tb.size()
    print (m.name)

print (nvertices, ntriangles)


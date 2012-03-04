import time
from renmas2.core import Ply

pl_reader = Ply()

start = time.clock()
#pl_reader.load("I:/Ply_files/cube.ply")
#pl_reader.load("I:/Ply_files/Horse97K.ply")
#pl_reader.load("I:/Ply_files/dragon_vrip.ply")
#pl_reader.load("I:/Ply_files/xyzrgb_dragon.ply")
#pl_reader.load("I:/Ply_files/g3.ply")
pl_reader.load("I:/Ply_files/lucy.ply")
end = time.clock()
print("Loading time = ", end-start)
vb = pl_reader._vertex_buffer
print(vb.size())
pl_reader.show_header()

for i in range(1):
    print(vb.get(i))

tb = pl_reader._triangle_buffer
print(tb.size())

for i in range(10):
    print(tb.get(i))

start = time.clock()
print("Bbox", vb.bbox())
print(time.clock()-start)


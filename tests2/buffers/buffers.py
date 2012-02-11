
from renmas2.core import VertexBuffer, VertexNBuffer, TriangleBuffer
from renmas2.core import TriangleNBuffer, FlatTriangleBuffer, FlatTriangleNBuffer, SmoothTriangleBuffer


vb = VertexBuffer()
vbn = VertexNBuffer()

vb.add(2.2,3.3,4)
vb.add(2.2,4.3,8)
vb.edit(1, 3,3,3)
#vb.clear()
print(vb.get(1))

vbn.add(5,6,7,7,8,9)
vbn.add(5,3,8,1,0,9)
vbn.edit(1, 3,3,3,3,3,3)
print(vbn.get(1))
print(vb.size())
print(vb.item_size())
print(vb.addr())
print(vbn.addr())

tb = TriangleBuffer()
tb.add(4,5,6)
tb.edit(0, 6,6,6)
print(tb.get(0))

tbn = TriangleNBuffer()
for i in range(50):
    tbn.add(7,7,8, 1,1,2)
tbn.add(1,3,8, 1,1,2)
print(tbn.get(50))


flt = FlatTriangleBuffer()
flt.add((3,4,5), (1,1,1), (7,7,7))
flt.edit(0, (4,4,4), (7,5,4), (1,2,3))
print(flt.get(0))

fltn = FlatTriangleNBuffer()
fltn.add((3,3,3), (1,1,1), (9,9,33), (3,3,4.5))
fltn.edit(0, (2,2,2), (1,1,5), (9,6,4), (0,1,3))
print(fltn.get(0))

smt = SmoothTriangleBuffer()
smt.add((1,1,2), (4,5,6), (2,4,6), (8,8,8), (0,2,3), (3,4,5))
smt.edit(0, (0,0,2), (3,3,3), (2,2,2), (8,8,8), (4,4,99), (1,1,1.22))
print(smt.get(0))


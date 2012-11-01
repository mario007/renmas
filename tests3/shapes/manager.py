
from renmas3.base import Vector3
from renmas3.shapes import ShapeManager, Triangle

v0 = Vector3(2.2, 4.4, 6.6)
v1 = Vector3(1.1, 1.1, 1.1)
v2 = Vector3(5.1, -1.1, 5.1)

t = Triangle(v0, v1, v2)
t2 = Triangle(v0, v1, v2)

mgr = ShapeManager()
mgr.add('t1', t)
mgr.add('t2', t2)

print(mgr.address_info(t))

for s in mgr:
    print (s)

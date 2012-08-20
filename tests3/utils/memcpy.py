
from array import array
import renmas3.core
from renmas3.utils import memcpy

#64-bit urgent TODO 
arr = array('f')
arr.append(5)
arr.append(9)

arr2 = array('f')
arr2.append(59)
arr2.append(79)

print("Before memcopy")
print(arr)
print(arr2)

adr, nelem = arr.buffer_info()
adr2, nelem2 = arr2.buffer_info()

memcpy(adr2, adr, 8)

print("After copying first array on second array")
print(arr)
print(arr2)


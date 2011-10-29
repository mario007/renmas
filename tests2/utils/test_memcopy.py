
import array
import renmas2.utils

#64-bit urgent TODO 
arr = array.array('f')
arr.append(5)
arr.append(9)

arr2 = array.array('f')
arr2.append(59)
arr2.append(79)

print("Before memcopy")
print(arr)
print(arr2)

adr, nelem = arr.buffer_info()
adr2, nelem2 = arr2.buffer_info()

renmas2.utils.memcpy(adr2, adr, 8)

print("After memcopy")
print(arr)
print(arr2)



from renmas3.base import FloatArray, FloatArray2D


arr = FloatArray(values=[4,5,6,7,8])
arr.append(3)
arr.extend((9,9,99,1,2,4))
print(arr[10])
print(len(arr))
print(arr[2])

arr2 = FloatArray2D(3, 4)
arr2[2,2] = 3
print(arr2[2,2])

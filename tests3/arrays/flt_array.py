
from renmas3.base import FloatArray


arr = FloatArray(values=[4,5,6,7,8])
arr.append(3)
arr.extend((9,9,99,1,2,4))
print(arr[10])
print(len(arr))

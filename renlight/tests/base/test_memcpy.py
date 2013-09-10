
import unittest
from array import array
from renlight.memcpy import memcpy

class MemcpyTest(unittest.TestCase):
    def test_cpy_arr(self):
        arr = array('f')
        arr.append(5)
        arr.append(9)

        arr2 = array('f')
        arr2.append(59)
        arr2.append(79)

        sa, nelem = arr.buffer_info()
        da, nelem2 = arr2.buffer_info()

        memcpy(da, sa, 8)
        self.assertAlmostEqual(arr[0], arr2[0])
        self.assertAlmostEqual(arr[1], arr2[1])

if __name__ == "__main__":
    unittest.main()

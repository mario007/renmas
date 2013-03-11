
import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Vector3


class NormalizeTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_arith1(self):

        code = """
vec1 = normalize(vec2)
        """
        vec1 = Vector3(0.0, 0.0, 0.0)
        vec2 = Vector3(0.3, 0.4, 0.5)
        props = {'vec1':vec1, 'vec2':vec2}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        vec2.normalize()
        val = bs.shader.get_value('vec1')
        self.assertAlmostEqual(val.x, vec2.x, 4)
        self.assertAlmostEqual(val.y, vec2.y, 4)
        self.assertAlmostEqual(val.z, vec2.z, 4)

if __name__ == "__main__":
    unittest.main()

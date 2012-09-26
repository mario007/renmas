
import unittest
from tdasm import Runtime
import renmas3.osl
from renmas3.osl import create_shader, create_argument
from renmas3.core import Vector3

class AssignConstTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_int(self):
        a1 = create_argument('p1', 2)
        args = {a1.name:a1}
        code = "p1 = 4"
        shader = create_shader(code, args)
        runtimes = [Runtime()]
        shader.prepare(runtimes)
        shader.execute()
        self.assertIsInstance(shader.get_value("p1"), int)
        self.assertEqual(shader.get_value('p1'), 4)

    def test_float(self):
        a1 = create_argument('p1', 2.0)
        a2 = create_argument('p2', 2.0)
        args = {a1.name:a1, a2.name:a2}
        code = """
p1 = 4.4
p2 = 8
        """
        shader = create_shader(code, args)
        runtimes = [Runtime()]
        shader.prepare(runtimes)
        shader.execute()
        self.assertIsInstance(shader.get_value("p1"), float)
        self.assertIsInstance(shader.get_value("p2"), float)
        self.assertAlmostEqual(shader.get_value("p1"), 4.4, places=5)
        self.assertAlmostEqual(shader.get_value("p2"), 8.0, places=5)

    def test_vector3(self):
        a1 = create_argument('p1', (4,5,6))
        a2 = create_argument('p2', [1,1,1])
        args = {a1.name:a1, a2.name:a2}
        code = """
p1 = [2, 4.4, 7] 
p2 = (11, 33, 1.1) 
        """
        shader = create_shader(code, args)
        runtimes = [Runtime()]
        shader.prepare(runtimes)
        shader.execute()
        v1 = shader.get_value("p1")
        v2 = shader.get_value("p2")
        self.assertIsInstance(v1, Vector3)
        self.assertIsInstance(v2, Vector3)

        self.assertAlmostEqual(v1.x, 2.0, places=5)
        self.assertAlmostEqual(v1.y, 4.4, places=5)
        self.assertAlmostEqual(v1.z, 7.0, places=5)
        self.assertAlmostEqual(v2.x, 11.0, places=5)
        self.assertAlmostEqual(v2.y, 33.0, places=5)
        self.assertAlmostEqual(v2.z, 1.1, places=5)
    

if __name__ == "__main__":
    unittest.main()


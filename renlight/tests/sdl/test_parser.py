
import unittest
from renlight.sdl.parser import parse
from renlight.sdl.stms import StmAssign, StmIf, StmReturn, StmWhile, StmEmpty


class ParserTest(unittest.TestCase):
    def test_parse(self):
        text = """
a = 33
g = f()
if b:
    a = 22
return 1
while 66:
    b = 55
pass

        """
        stms = parse(text)
        self.assertTrue(isinstance(stms[0], StmAssign))
        self.assertTrue(isinstance(stms[1], StmAssign))
        self.assertTrue(isinstance(stms[2], StmIf))
        self.assertTrue(isinstance(stms[3], StmReturn))
        self.assertTrue(isinstance(stms[4], StmWhile))
        self.assertTrue(isinstance(stms[5], StmEmpty))

if __name__ == "__main__":
    unittest.main()


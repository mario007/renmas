
import unittest
from random import random
from tdasm import Runtime
import renmas2

ren = renmas2.Renderer()
filename = 'I:\\projekt1.renmas'
ren.save_project(filename)

ren._width = 55
ren.load_project(filename)
print(ren._width)


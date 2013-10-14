
import unittest
from unittest import TestLoader
suite = TestLoader().discover('base')
suite.addTests(TestLoader().discover('sdl'))
suite.addTests(TestLoader().discover('shapes'))
unittest.TextTestRunner(verbosity=5).run(suite)

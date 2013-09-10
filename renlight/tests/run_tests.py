
import unittest
loader = unittest.TestLoader()
suite = loader.discover('base')
#suite.addTests(loader.discover('base'))
unittest.TextTestRunner(verbosity=3).run(suite)

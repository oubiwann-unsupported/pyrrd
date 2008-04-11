import unittest
import doctest

from utils import importModule

# to add a new module to the test runner, simply include is in the list below:
modules = [
    'pyrrd.rrd',
    'pyrrd.external',
    'pyrrd.graph',
    'pyrrd.utils',
]

suite = unittest.TestSuite()

for modname in modules:
    mod = importModule(modname)
    suite.addTest(doctest.DocTestSuite(mod))

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)



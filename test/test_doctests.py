from doctest import DocFileSuite

from utils import buildDoctestSuite


# to add a new module to the test runner, simply include is in the list below:
modules = [
    "pyrrd.external",
    "pyrrd.graph",
    "pyrrd.node",
    "pyrrd.rrd",
    "pyrrd.util",
    "pyrrd.util.dist",
]

suites = [DocFileSuite("../README")]
if modules:
    suites.append(buildDoctestSuite(modules))


if __name__ == "__main__":
    import unittest
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(unittest.TestSuite(suites))



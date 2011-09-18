"""
Utility functions for testing.
"""
import doctest
import glob
import os
import tempfile
import unittest
from StringIO import StringIO


def importModule(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def fileIsTest(path, skipFiles=[]):
    if not os.path.isfile(path):
        return False
    filename = os.path.basename(path)
    if filename in skipFiles:
        return False
    if filename.startswith('test') and filename.endswith('.py'):
        return True


def find(start, func, skip=[]):
    for item in [os.path.join(start, x) for x in os.listdir(start)]:
        if func(item, skip):
            yield item
        if os.path.isdir(item):
            for subItem in find(item, func, skip):
                yield subItem


def findTests(startDir, skipFiles=[]):
    return find(startDir, fileIsTest, skipFiles)


def buildDoctestSuite(modules):
    suite = unittest.TestSuite()
    for modname in modules:
        mod = importModule(modname)
        suite.addTest(doctest.DocTestSuite(mod))
    return suite


def buildUnittestSuites(paths=[], skip=[]):
    """
    paths: a list of directories to search
    skip: a list of file names to skip
    """
    suites = []
    loader = unittest.TestLoader()
    for startDir in paths:
        for testFile in findTests(startDir, skip):
            modBase = os.path.splitext(testFile)[0]
            name = modBase.replace(os.path.sep, '.')
            # import the testFile as a module
            mod = importModule(name)
            # iterate through module objects, checking for TestCases
            for objName in dir(mod):
                if not objName.endswith('TestCase'):
                    continue
                obj = getattr(mod, objName)
                if not issubclass(obj, unittest.TestCase):
                    continue
                # create a suite from any test cases
                suite = loader.loadTestsFromTestCase(obj)
                # append to suites list
                suites.append(suite)
    return suites


def runDocTests(path):
    paths = glob.glob(path)
    suites = []
    for path in paths:
        path = os.path.abspath(path)
        suites.extend(doctest.DocFileSuite(
            path, module_relative=False, optionflags=doctest.ELLIPSIS))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(unittest.TestSuite(suites))


def assembleAndRunDocTests(path):
    """
    This function assembles all the pattern files together into a single
    temporary file. This is done in order to avoide entering duplicate code in
    each pattern file.
    """
    filenames = sorted(glob.glob(path))
    text = StringIO()
    [text.write(open(filename).read()) for filename in filenames]
    fileHandle, tempFilename = tempfile.mkstemp(
        suffix=".txt", prefix="assembled-patterns-doctests-tmp", text=True)
    os.write(fileHandle, text.getvalue())
    suites = [doctest.DocFileSuite(
        tempFilename, module_relative=False, optionflags=doctest.ELLIPSIS)]
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(unittest.TestSuite(suites))
    os.unlink(tempFilename)

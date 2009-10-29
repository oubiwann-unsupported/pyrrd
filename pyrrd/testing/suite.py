"""
Utility functions for testing.
"""
import os
import unittest
import doctest


def importModule(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def fileCheck(path, skipFiles=[]):
    if not os.path.isfile(path):
        return False
    filename = os.path.basename(path)
    if filename in skipFiles:
        return False
    if path in skipFiles:
        print "skip it!"
        return False
    return True


def fileIsTest(path, skipFiles=[]):
    result = fileCheck(path, skipFiles)
    if not result:
        return False
    filename = os.path.basename(path)
    if filename.startswith('test') and filename.endswith('.py'):
        return True


def fileHasDoctests(path, skipFiles=[]):
    result = fileCheck(path, skipFiles)
    if result and path.endswith('.py'):
        fh = open(path)
        if '>>>' in fh.read():
            result = True
        else:
            result = False
        fh.close()
    else:
        result = False
    return result


def find(start, func, skip=[]):
    for item in [os.path.join(start, x) for x in os.listdir(start)]:
        if func(item, skip):
            yield item
        if os.path.isdir(item):
            for subItem in find(item, func, skip):
                yield subItem


def findTests(startDir, skipFiles=[]):
    return find(startDir, fileIsTest, skipFiles)


def findDoctests(startDir, skipFiles=[]):
    return find(startDir, fileHasDoctests, skipFiles)


def _buildDoctestSuiteFromModules(modules, skip):
    suite = unittest.TestSuite()
    for modname in modules:
        mod = importModule(modname)
        if mod not in skip:
            suite.addTest(doctest.DocTestSuite(mod))
    return suite


def _buildDoctestSuiteFromFiles(files, skip):
    suite = []
    for file in files:
        if file not in skip:
            suite.append(DocFileSuite(file))
    return suite

def _buildDoctestSuiteFromPaths(paths=[], skip=[]):
    """
    paths: a list of directories to search
    skip: a list of file names to skip
    """
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for startDir in paths:
        for testFile in findDoctests(startDir, skip):
            modBase = os.path.splitext(testFile)[0]
            name = modBase.replace(os.path.sep, '.')
            if name in skip:
                continue
            mod = importModule(name)
            suite.addTest(doctest.DocTestSuite(mod))
    return suite

def buildDoctestSuites(modules=[], files=[], paths=[], skip=[]):
    suite = []
    if modules:
        suite.extend(_buildDoctestSuiteFromModules(modules, skip))
    if files:
        suite.extend(_buildDoctestSuiteFromFiles(files, skip))
    if paths:
        suite.extend(_buildDoctestSuiteFromPaths(paths, skip))
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

#!/usr/bin/env python
import os
from unittest import TestSuite
from unittest import TextTestRunner
from doctest import DocFileSuite

from utils import findTests, importModule, buildUnittestSuites

from test_doctests import suites as doctestSuite


searchDirs = ['pyrrd', 'test']
skipFiles = ['test_doctests.py', 'test_all.py']

# XXX once we have unittest tests, we'll uncomment this next line
suites = buildUnittestSuites(paths=searchDirs, skip=skipFiles)
suites.extend(doctestSuite)

if __name__ == '__main__':
    runner = TextTestRunner(verbosity=2)
    runner.run(TestSuite(suites))

#!/usr/bin/env python
from unittest import TestSuite, TextTestRunner
from doctest import DocFileSuite

from pyrrd import meta
from pyrrd.testing.suite import (
    findTests, importModule, buildUnittestSuites, buildDoctestSuites)


searchDirs = [meta.library_name]
skips = []
suites = buildUnittestSuites(paths=searchDirs, skip=skips)
docFiles = [
    DocFileSuite("README"),
    ]
suites.extend(docFiles)
suites.extend(buildDoctestSuites(paths=searchDirs, skip=skips))

if __name__ == '__main__':
    runner = TextTestRunner(verbosity=2)
    runner.run(TestSuite(suites))

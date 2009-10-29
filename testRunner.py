#!/usr/bin/env python
"""
    %prog [options]
"""
from doctest import DocFileSuite
from optparse import OptionParser
from unittest import TestSuite, TextTestRunner

from pyrrd import meta
from pyrrd.testing.suite import (
    findTests, importModule, buildUnittestSuites, buildDoctestSuites)


def getSuites(skips):
    searchDirs = [meta.library_name]
    suites = buildUnittestSuites(paths=searchDirs, skip=skips)
    docFiles = [
        DocFileSuite("README"),
        ]
    suites.extend(docFiles)
    suites.extend(buildDoctestSuites(paths=searchDirs, skip=skips))
    return suites

if __name__ == '__main__':
    parser = OptionParser(__doc__)
    parser.add_option(
        "-s", "--skip", help=(
            "Provide a comma-separated (no spaces) list of file names "
            "relative path name names, or full module names to skip. "
            "The following are valid values for SKIP: "
            "  bindings.py,rrd.py OR "
            "  ./pyrrd/backend/bindings.py,./pyrrd/rrd.py OR "
            "  pyrrd.backend.bindings,pyrrd.rrd. "
            "Also note that the various types of skips can be combined: "
            "  bindings.py,./pyrrd/rrd.py,pyrrd.graph"))
    parser.add_option(
        "-v", "--verbosity", help=(
            "Set the verbosity of the test "
            "output. Default value is 2."))
    options, args = parser.parse_args()
    if options.skip:
        skips = options.skip.split(",")
        cleanedSkips = []
        for skip in skips:
            if skip.startswith("./"):
                skip = skip.replace("./", "")
            cleanedSkips.append(skip)
        skips = cleanedSkips
    else:
        skips = []
    verbosity = options.verbosity or 2
    runner = TextTestRunner(verbosity=verbosity)
    runner.run(TestSuite(getSuites(skips)))

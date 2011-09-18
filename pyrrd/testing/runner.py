import optparse
import os
import unittest

from pyrrd import meta
from pyrrd.testing import result


class CustomTestRunner(unittest.TextTestRunner):
    """
    This is only needed for Python 2.6 and lower.
    """
    def _makeResult(self):
        return result.CustomTestResult(
            self.stream, self.descriptions, self.verbosity)


def discover(loader, top_level_directory):
    names = []
    def _path_to_module(path):
        # generate dotted names for file paths
        path = path.replace(".py", "")
        return path.replace("/", ".")

    # walk the directory
    for dirpath, dirnames, filenames in os.walk(top_level_directory):
        modules = [
            _path_to_module(os.path.join(dirpath, x)) for x in filenames
                if x.startswith("test_") and x.endswith(".py")]
        if not modules:
            continue
        names.extend(modules)
    return loader.loadTestsFromNames(names)


def get_suite(loader, top_level_directory, options):
    print options.test_specific
    if options.test_specific:
        suite = loader.loadTestsFromName(options.test_specific)
    elif hasattr(loader, "discover"):
        # Python 2.7
        suite = loader.discover(top_level_directory)
    else:
        # Python 2.4, 2.5, 2.6
        suite = discover(loader, top_level_directory)
    return suite


def get_runner():
    try:
        # Python 2.7
        runner = unittest.TextTestRunner(
            verbosity=2, resultclass=result.CustomTestResult)
    except TypeError:
        # Python 2.4, 2.5, 2.6
        runner = CustomTestRunner(verbosity=2)
    return runner


def run_tests(options):
    loader = unittest.TestLoader()
    suite = get_suite(loader, meta.library_name, options)
    get_runner().run(suite)


def main():
    parser = optparse.OptionParser()
    parser.add_option("--test-specific", dest="test_specific")
    (options, args) = parser.parse_args()
    run_tests(options)


if __name__ == "__main__":
    main()

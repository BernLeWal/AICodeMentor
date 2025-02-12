"""UnitTests for the application."""
# This __init__.py file allows the test directory to be recognized as a package

import unittest

def load_tests(loader, standard_tests, pattern):
    """Auto-discover and load all test cases in the current package."""
    if pattern is None:
        pattern = 'test_*.py'  # Ensure it only loads test files following naming convention
    test_suite = loader.discover(start_dir=__path__[0], pattern=pattern)
    standard_tests.addTests(test_suite)
    return standard_tests

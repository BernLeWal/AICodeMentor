#!/bin/python
"""Run the full test-suite"""

import unittest

# Discover and run all test cases in the "tests" directory
test_loader = unittest.TestLoader()
test_suite = test_loader.discover("test")

test_runner = unittest.TextTestRunner()
test_runner.run(test_suite)

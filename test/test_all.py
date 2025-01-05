#!/bin/python
"""UnitTests for all"""

# test/agents/test_AIAgent.py
import unittest
#import json

# Add the parent directory to the sys.path in order to avoid module import errors
#import os
#import sys
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

class TestAll(unittest.TestCase):
    """UnitTests for all"""
    def setUp(self):
        pass

    def test_all(self):
        """A placeholder test that always passes."""
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()

#!/bin/python
import logging
import unittest

# Setup logging framework
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



if __name__ == "__main__":
    unittest.main()

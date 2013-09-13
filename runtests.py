"""Run all tests auto discovered by unittest.TestLoader"""

import unittest
import sys


if __name__ == "__main__":
    all_tests = unittest.TestLoader().discover('test')
    verbosity = 1
    for argv in sys.argv:
        if "-v" in argv:
            verbosity = argv.count("v") + 1
    unittest.TextTestRunner(verbosity=verbosity).run(all_tests)

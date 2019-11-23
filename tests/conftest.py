"""
Common pytest configuration for the test suites
"""

import os
import sys

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, '..', 'src'))

pytest_plugins = 'sphinx.testing.fixtures'

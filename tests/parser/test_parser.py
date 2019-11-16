"""
Test the parsing of C files into the needed pieces.
"""
import os

from c_docs import parser

SCRIPT_DIR = os.path.dirname(__file__)
def test_basic_file_parsing():
    """
    Test that a simple C file is turned into 2 sections one for the module level
    comment and one for the function level comment
    """
    comments = parser.parse(os.path.join(SCRIPT_DIR, 'assets', 'one_function.c'))
    assert comments == ["This is a file comment", "This is a function comment"]

def test_alternate_file_parsing():
    """
    Test that a simple C file is turned into 2 sections one for the module level
    comment and one for the function level comment
    """
    comments = parser.parse(os.path.join(SCRIPT_DIR, 'assets', 'typedef.c'))
    assert comments == ["This is a file comment", "This is a type comment",
                        "This is a function comment"]

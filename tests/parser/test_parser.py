"""
Test the parsing of C files into the needed pieces.
"""
import os
import pytest

from c_docs import parser

SCRIPT_DIR = os.path.dirname(__file__)
testdata = [('one_function.c', ["This is a file comment", "This is a function comment"]),
            ('typedef.c', ["This is a file comment", "This is a type comment", "This is a function comment"]),
           ]


@pytest.mark.parametrize('filename, expected', testdata)
def test_basic_file_parsing(filename, expected):
    """
    Test that a simple C file is turned into 2 sections one for the module level
    comment and one for the function level comment
    """
    comments = parser.parse(os.path.join(SCRIPT_DIR, 'assets', filename))
    assert comments == expected

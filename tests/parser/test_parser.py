"""
Test the parsing of C files into the needed pieces.
"""
import json
import os
import pytest

from c_docs import parser

SCRIPT_DIR = os.path.dirname(__file__)
testdata = [('one_function.c', {'doc': 'This is a file comment',
                                'name': 'one_function.c',
                                'type': 'file',
                                'children': [
                                    {'doc': 'This is a function comment',
                                     'name': 'my_func',
                                     'type': 'function',
                                     # 'signature': 'my_func(void)'
                                     }]}),
            ('typedef.c', {'doc': 'This is a file comment',
                           'name': 'typedef.c',
                           'type': 'file',
                           'children': [
                               {'doc': 'This is a type comment',
                                'name': 'unknown_member',
                                'type': 'struct'},
                               {'doc': 'This is a function comment',
                                'name': 'my_func',
                                'type': 'function',
                                # 'signature': 'my_func(void)'
                                }]}),
           ]


@pytest.mark.parametrize('filename, expected', testdata)
def test_basic_file_parsing(filename, expected):
    """
    Test that a simple C file is turned into 2 sections one for the module level
    comment and one for the function level comment
    """
    doc_item = parser.parse(os.path.join(SCRIPT_DIR, 'assets', filename))
    assert json.loads(str(doc_item)) == expected

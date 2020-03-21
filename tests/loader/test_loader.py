"""
Test the loading of C files into the needed pieces.
"""
import json
import os
import pytest

from sphinx_c_autodoc import loader

SCRIPT_DIR = os.path.dirname(__file__)
testdata = [
    (
        "one_function.c",
        {
            "doc": "This is a file comment",
            "name": "one_function.c",
            "type": "file",
            "start_line": 1,
            "end_line": 17,
            "children": [
                {
                    "doc": "This is a function comment",
                    "name": "my_func",
                    "type": "function",
                    "start_line": 7,
                    "end_line": 16,
                }
            ],
        },
    ),
    (
        "typedef.c",
        {
            "doc": "This is a file comment",
            "name": "typedef.c",
            "type": "file",
            "start_line": 1,
            "end_line": 25,
            "children": [
                {
                    "doc": "This is a type comment",
                    "name": "unknown_member",
                    "type": "struct",
                    "start_line": 7,
                    "end_line": 13,
                    "children": [
                        {
                            "doc": "",
                            "name": "foo",
                            "type": "member",
                            "start_line": 12,
                            "end_line": 12,
                        }
                    ],
                },
                {
                    "doc": "This is a function comment",
                    "name": "my_func",
                    "type": "function",
                    "start_line": 15,
                    "end_line": 24,
                },
            ],
        },
    ),
]


@pytest.mark.parametrize("filename, expected", testdata)
def test_basic_file_loading(filename, expected):
    """
    Test that a simple C file is turned into 2 sections one for the module level
    comment and one for the function level comment
    """
    fullname = os.path.join(SCRIPT_DIR, "assets", filename)
    with open(fullname) as f:
        contents = f.read()
    doc_item = loader.load(fullname, contents)
    assert json.loads(str(doc_item)) == expected


def test_basic_file_loading_grabbed_twice():
    """
    Some attributes are initialized to None and then cached, this gets
    coverage of the cache now being filled out.
    """
    filename, expected = testdata[0]
    fullname = os.path.join(SCRIPT_DIR, "assets", filename)
    with open(fullname) as f:
        contents = f.read()
    doc_item = loader.load(fullname, contents)
    ast = str(doc_item)

    # second call getting the cached version of some things.
    ast = str(doc_item)
    assert json.loads(ast) == expected

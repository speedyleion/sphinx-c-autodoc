"""
Performs end to end testing of the c extension
"""
import os
from sphinx.cmd.build import main


SCRIPT_DIR = os.path.dirname(__file__)
def test_autodoc_of_c_file(tmp_path):
    """
    Tests the creation of the documented C file.
    """
    source_dir = os.path.join(SCRIPT_DIR, 'assets')
    main(['-a', source_dir, str(tmp_path)])

    file_name = tmp_path / 'example.html'
    with file_name.open() as f:
        contents = f.read()

    assert 'This is a file comment' in contents

    file_name = tmp_path / 'file_2.html'
    with file_name.open() as f:
        contents = f.read()

    # Not ideal but sphinx takes a while to run...
    assert 'This is file 2' in contents
    assert 'It has a multi-line comment' in contents
    assert 'unknown_member' in contents

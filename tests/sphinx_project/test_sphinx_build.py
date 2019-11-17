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

    assert 'Hello What is Up?' in contents

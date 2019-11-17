"""
Performs end to end testing of the c extension
"""
import os
import sphinx

SCRIPT_DIR = os.path.dirname(__file__)
def test_autodoc_of_c_file():
    """
    Tests the creation of the documented C file.
    """
    source_dir = os.path.join(SCRIPT_DIR, 'assets')
    output_dir = os.path.join(SCRIPT_DIR, 'assets', '_build')
    sphinx.main(['-a', source_dir, output_dir])
    with open(os.path.join(output_dir, 'foo.html'), 'r') as f:
        contents = f.read()

    assert 'hello' in contents

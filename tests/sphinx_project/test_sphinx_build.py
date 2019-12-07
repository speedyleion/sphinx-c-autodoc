"""
Performs end to end testing of the c extension

For all of these tests warnigns are treated as errors so that any warnings
from bad logic can more easily be seen in the test output
"""
import os
import shutil
from sphinx.cmd.build import main


SCRIPT_DIR = os.path.dirname(__file__)

def test_autodoc_of_c_file(tmp_path):
    """
    Tests the creation of the documented C file.
    """
    source_dir = os.path.join(SCRIPT_DIR, '..', 'assets')
    main(['-a', '-E', '-W', source_dir, str(tmp_path)])

    file_name = tmp_path / 'example.html'
    with file_name.open() as f:
        contents = f.read()

    assert 'This is a file comment' in contents

    # Check for anonymouse enumerations
    assert 'anon_example_' in contents

    file_name = tmp_path / 'file_2.html'
    with file_name.open() as f:
        contents = f.read()

    # Not ideal but sphinx takes a while to run...
    assert 'This is file 2' in contents
    assert 'It has a multi-line comment' in contents
    assert 'unknown_member' in contents

def test_incremental_build_updates_docs(tmp_path):
    """
    Tests the output is updated if one of the input files to document is
    changed.
    """
    original_source_dir = os.path.join(SCRIPT_DIR, '..', 'assets')

    # Copy over all the documentation source files as this is going to modify
    # one of them
    new_source_path = tmp_path / 'assets'
    new_source_dir = str(new_source_path)
    shutil.copytree(original_source_dir, new_source_dir)

    output_path = tmp_path / '_build'

    # Use `-a`, `-E` initially to ensure an initial full clean build
    main(['-a', '-E', '-W', new_source_dir, str(output_path)])

    file_name = output_path / 'example.html'
    with file_name.open() as f:
        contents = f.read()

    new_expected_contents = 'A new update to a file.'

    # Pre-condition check, if this isn't True then the next check may be
    # invalid.
    assert 'This is a file comment' in contents
    assert new_expected_contents not in contents

    source_name = new_source_path / 'c_source' / 'example.c'
    with source_name.open('w') as f:
        f.write(f'/** {new_expected_contents} */')

    main(['-W', new_source_dir, str(output_path)])

    with file_name.open() as f:
        contents = f.read()

    assert new_expected_contents in contents
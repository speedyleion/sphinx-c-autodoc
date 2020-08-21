"""
View code is basically a post processing of a parsed document tree.
In order to more easily test this it generates an entire sphinx project and
then the resultant html files are analyzed to ensure they have the right
content.

For all of these tests warnigns are treated as errors so that any warnings
from bad logic can more easily be seen in the test output
"""
import re
import os
from sphinx.cmd.build import main


SCRIPT_DIR = os.path.dirname(__file__)


def test_viewcode_of_sphinx_project(tmp_path):
    """
    Tests the insertion of hyperlinks between documentation and code.

    This isn't ideal to have all asserts in one function, but to keep the
    overall test run times down it is done this way.
    """
    source_dir = os.path.join(SCRIPT_DIR, "..", "assets")
    # With sphinx 3 it will throw a warning for duplicate declarations, even with no
    # index usage, so allow warnings in this test.
    main(
        [
            "-a",
            "-E",
            "-D",
            "exclude_patterns=[]",
            "-D",
            "master_doc=viewcode_index",
            source_dir,
            str(tmp_path),
        ]
    )
    file_name = tmp_path / "example.html"
    with file_name.open() as f:
        contents = f.read()

    chosen_links = (
        '<dt id="c.MY_COOL_MACRO">',
        '<a class="reference internal" href="_modules/example.c.html#c.MY_COOL_MACRO"><span class="viewcode-link">[source]</span></a>',
        '<dt id="c.members_documented_with_napoleon.two.nested_two">',
        '<a class="reference internal" href="_modules/example.c.html#c.members_documented_with_napoleon.two.nested_two"><span class="viewcode-link">[source]</span></a>',
    )
    for l in chosen_links:
        assert l in contents

    file_name = tmp_path / "sub_dir" / "file_2.html"
    with file_name.open() as f:
        contents = f.read()

    chosen_links = (
        '<a class="reference internal" href="../_modules/file_2.c.html#c.unknown_member.foo"><span class="viewcode-link">[source]</span></a>',
    )
    for l in chosen_links:
        assert l in contents

    # Test the back links
    file_name = tmp_path / "_modules" / "example.c.html"
    with file_name.open() as f:
        contents = f.read()

    chosen_links = (
        '<div class="viewcode-block" id="c.members_documented_with_napoleon.two.nested_two"><a class="viewcode-back" href="../example.html#c.members_documented_with_napoleon.two.nested_two">[docs]</a>',
        '<div class="viewcode-block" id="c.MY_COOL_MACRO"><a class="viewcode-back" href="../example.html#c.MY_COOL_MACRO">[docs]</a>',
    )
    for l in chosen_links:
        assert l in contents

    # Test normal C constructs elsewhere in docs
    file_name = tmp_path / "viewcode.html"
    with file_name.open() as f:
        contents = f.read()

    chosen_links = (
        '<a class="reference internal" href="_modules/example.c.html#c.napoleon_documented_function"><span class="viewcode-link">[source]</span></a>',
        # One needs to use noindex in order to avoid sphinx warning and once
        # one uses noindex then the permalinks are no longer generated :(
        # '<a class="headerlink" href="#c.napoleon_documented_function" title="Permalink to this definition">',
    )
    for l in chosen_links:
        assert l in contents

    # Ensure only the one function that actually had a source file to be able to link to creates a link
    link_count = len(re.findall("viewcode-link", contents))
    assert link_count == 1

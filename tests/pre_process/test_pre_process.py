"""
Test the pre-parse hook
"""
from textwrap import dedent

from sphinx.ext.autodoc.directive import AutodocDirective

NEW_FILE_CONTENTS = """\
    /**
     * A comment for a variable that doesn't exist in original file
     */
    static int compilation_db_define;
    """

new_contents_int = """\
    static int compilation_db_define
    A comment for a variable that doesn't exist in original file"""


def pre_parser(app, filename, contents, *args):
    """
    Implements the pre-parsing implementation.
    """
    contents[:] = [NEW_FILE_CONTENTS]


def test_pre_parsing(sphinx_state):
    """
    Tests the restructured text output returned by the directive.
    """
    sphinx_state.env.app.connect("c-autodoc-pre-process", pre_parser)
    directive = AutodocDirective(
        "autocdata",
        ["variables.c::compilation_db_define"],
        {"members": None},
        None,
        None,
        None,
        None,
        sphinx_state,
        sphinx_state.state_machine,
    )
    output = directive.run()

    # First item is the index entry
    assert 2 == len(output)
    body = output[1]

    # For whatever reason the as text comes back with double spacing, so we
    # knock it down to single spacing to make the expected string smaller.
    assert dedent(new_contents_int) == body.astext().replace("\n\n", "\n")

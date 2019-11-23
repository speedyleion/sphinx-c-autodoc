"""
Test autoctype directive
"""
from textwrap import dedent

import pytest

from sphinx.ext.autodoc.directive import AutodocDirective


class TestAutoCType:
    """
    Testing class for the autoctype directive
    """
    my_int = """\
        my_int
        This is basic typedef from a native type to another name."""

    my_struct_type = """\
        my_struct_type
        A struct that is actually anonymouse but is typedefed in place.

        bar


        baz
        """

    # Note the '*' around `not` are bold attributes in html so are stripped away
    # in the as_text()
    some_struct = """\
        some_struct
        A plain struct that is not typedefed.

        foo


        a
        """

    typedefed_struct = """\
        typedefed_struct
        A typedef of a struct after the fact."""

    # This will have the title and a newline, but no content as it didn't exist
    undocumented = """\
        undocumented
        """
    documented_members = """\
        documented_members
        A struct with documented members

        a
        The string for member a

        b
        Some other string for member b"""

    doc_data = [
        ('types.c::my_int', my_int),
        ('types.c::my_struct_type', my_struct_type),
        ('types.c::some_struct', some_struct),
        ('types.c::typedefed_struct', typedefed_struct),
        ('types.c::undocumented', undocumented),
        ('types.c::documented_members', documented_members),
    ]

    @pytest.mark.parametrize('type_, expected_doc', doc_data)
    def test_doc(self, type_, expected_doc, sphinx_state):
        """
        Tests the restructured text output returned by the directive.
        """
        directive = AutodocDirective('autoctype', [type_], {'members': None},
                                     None, None, None, None, sphinx_state, None)
        output = directive.run()

        # First item is the index entry
        assert 2 == len(output)
        body = output[1]

        # For whatever reason the as text comes back with double spacing, so we
        # knock it down to single spacing to make the expected string smaller.
        assert dedent(expected_doc) == body.astext().replace('\n\n', '\n')

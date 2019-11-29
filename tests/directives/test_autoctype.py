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
        typedef int my_int
        This is basic typedef from a native type to another name."""

    my_struct_type = """\
        struct my_struct_type
        A struct that is actually anonymouse but is typedefed in place.

        int bar
        The bar like member for bar like things. This is multiple lines to make
        sure the parsing logic is correct.

        float baz
        The baz like member"""

    # Note the '*' around `not` are bold attributes in html so are stripped away
    # in the as_text()
    some_struct = """\
        struct some_struct
        A plain struct that is not typedefed.

        my_struct_type foo


        int a
        """

    typedefed_struct = """\
        typedef intermediate_type typedefed_struct
        A typedef of a struct after the fact."""

    # This will have the title and a newline, but no content as it didn't exist
    undocumented = """\
        typedef char undocumented
        """

    documented_members = """\
        struct documented_members
        A struct with documented members

        float a
        The string for member a

        float b
        Some other string for member b"""

    a_union_type = """\
        union a_union_type
        A union type that can be documented

        float alias_a


        int alias_b
        """

    a_multiply_documented_union_type = """\
        union a_multiply_documented_union_type
        A union type that documents in multiple places, this tests a few things:
        Can one put the type in the napoleon documentation? It is undefined if the
        types don't match.
        Does the merging of the documentation successfully combine into multiple
        paragraphs?

        float alias_a
        The description for alias_a the napoleon style
        documentation includes the type.

        int alias_b
        This documentation lacks the type description but it will be taken
        from the declaration.
        A second paragraph for alias_b from the member declaration"""

    nested_struct = """\
        struct nested_struct
        A structure containing an inline declared structure field.

        int one
        The first member of parent struct

        struct two
        This is a structure declared in the parent struct its children are
        documented below.

        float nested_one
        The nested member documentation

        int nested_two
        The second nested member documentation

        float three
        The third member of parent struct"""


    doc_data = [
        ('types.c::my_int', my_int),
        ('types.c::my_struct_type', my_struct_type),
        ('types.c::some_struct', some_struct),
        ('types.c::typedefed_struct', typedefed_struct),
        ('types.c::undocumented', undocumented),
        ('types.c::documented_members', documented_members),
        ('types.c::a_union_type', a_union_type),
        ('types.c::a_multiply_documented_union_type', a_multiply_documented_union_type),
        ('types.c::nested_struct', nested_struct),
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

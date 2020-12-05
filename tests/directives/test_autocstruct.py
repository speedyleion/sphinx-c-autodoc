"""
Test autoctype directive
"""
from textwrap import dedent

import pytest

from sphinx.ext.autodoc.directive import AutodocDirective


class TestAutoCStruct:
    """
    Testing class for the autocstruct directive
    """

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
    # Also the members are flipped, this is due to the "by_source" default sorting of
    # https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_member_order
    some_struct = """\
        struct some_struct
        A plain struct that is not typedefed.

        int a


        my_struct_type foo
        """

    documented_members = """\
        struct documented_members
        A struct with documented members

        float a
        The string for member a

        float b
        Some other string for member b"""

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

    struct_with_array_member = """\
        struct struct_with_array_member
        A struct with an array inside
        
        int foo[10]
        An array member with an unknown type, it will show as int.
        
        float bar[10]
        An array with a known type."""

    doc_data = [
        ("types.c::my_struct_type", my_struct_type),
        ("types.c::some_struct", some_struct),
        ("types.c::documented_members", documented_members),
        ("types.c::nested_struct", nested_struct),
        ("types.c::struct_with_array_member", struct_with_array_member),
    ]

    @pytest.mark.parametrize("struct, expected_doc", doc_data)
    def test_doc(self, struct, expected_doc, sphinx_state):
        """
        Tests the restructured text output returned by the directive.
        """
        directive = AutodocDirective(
            "autocstruct",
            [struct],
            # Members of structs should be visible even with no private members.
            # I.e. if the struct is visible all of it is.
            {"members": None, "no-private-members": None},
            None,
            None,
            None,
            None,
            sphinx_state,
            None,
        )
        output = directive.run()

        # First item is the index entry
        assert 2 == len(output)
        body = output[1]

        # For whatever reason the as text comes back with double spacing, so we
        # knock it down to single spacing to make the expected string smaller.
        assert body.astext().replace("\n\n", "\n") == dedent(expected_doc)

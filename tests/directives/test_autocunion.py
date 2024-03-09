"""
Test autoctype directive
"""

from textwrap import dedent

import pytest

from sphinx.ext.autodoc.directive import AutodocDirective


class TestAutoCUnion:
    """
    Testing class for the autocunion directive
    """

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

    # Not fond of the int, but clang reduces it to this, need to find a way to
    # read those back when clang fails.
    a_union_typedef = """\
        union a_union_typedef
        A typedefed union

        int one


        int two
        """

    doc_data = [
        ("types.c::a_union_type", a_union_type),
        ("types.c::a_multiply_documented_union_type", a_multiply_documented_union_type),
        ("types.c::a_union_typedef", a_union_typedef),
    ]

    @pytest.mark.parametrize("union, expected_doc", doc_data)
    def test_doc(self, union, expected_doc, sphinx_state):
        """
        Tests the restructured text output returned by the directive.
        """
        directive = AutodocDirective(
            "autocunion",
            [union],
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
        assert body.astext().replace("\n\n", "\n") == dedent(expected_doc)

"""
Test the parsing of c data (variables) objects
"""
from textwrap import dedent

import pytest

from sphinx.ext.autodoc.directive import AutodocDirective


class TestAutoCData:
    """
    Testing class for the autocdata directive
    """

    file_level_variable = """\
        static const char *file_level_variable
        A variable"""

    inline_struct_variable = """\
        inline_struct_variable
        Even structures defined in variables can be handled.

        int a


        float b
        """

    doc_data = [
        ("variables.c::file_level_variable", file_level_variable),
        ("example.c::inline_struct_variable", inline_struct_variable),
    ]

    @pytest.mark.parametrize("variable, expected_doc", doc_data)
    def test_doc(self, variable, expected_doc, sphinx_state):
        """
        Tests the restructured text output returned by the directive.
        """
        directive = AutodocDirective(
            "autocdata",
            [variable],
            {"members": None},
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

    def test_incorrectly_specified_variable_causes_warning(self, sphinx_state):
        """
        Test that when a directive string is for an unparsable variable name
        a warning is thrown.
        """
        directive = AutodocDirective(
            "autocdata",
            ["example.c::unparseable-kabab"],
            {"members": None},
            None,
            None,
            None,
            None,
            sphinx_state,
            None,
        )

        output = directive.run()

        warnings = sphinx_state.env.app._warning.getvalue()

        messages = ("invalid signature for autocdata",)
        for message in messages:
            assert message in warnings

        assert [] == output

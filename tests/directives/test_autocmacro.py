"""
Test the parsing of c macro objects
"""
from textwrap import dedent

import pytest

from sphinx.ext.autodoc.directive import AutodocDirective


class TestAutoCMacro:
    """
    Testing class for the autocmacro directive
    """

    my_d_fine = """\
        MY_D_FINE
        A define of something."""

    documented_after = """\
        DOCUMENTED_AFTER
        A trailing item documentation"""

    undocumented_macro = """\
        UNDOCUMENTED_MACRO
        """

    function_like_macro = """\
        FUNCTION_LIKE_MACRO(_x, _y)
        A function like macro with 2 parameters"""

    doc_data = [
        ("macros.c::MY_D_FINE", my_d_fine),
        ("macros.c::DOCUMENTED_AFTER", documented_after),
        ("macros.c::UNDOCUMENTED_MACRO", undocumented_macro),
        ("macros.c::FUNCTION_LIKE_MACRO", function_like_macro),
    ]

    @pytest.mark.parametrize("macro, expected_doc", doc_data)
    def test_doc(self, macro, expected_doc, sphinx_state):
        """
        Tests the restructured text output returned by the directive.
        """
        directive = AutodocDirective(
            "autocmacro",
            [macro],
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
        assert dedent(expected_doc) == body.astext().replace("\n\n", "\n")

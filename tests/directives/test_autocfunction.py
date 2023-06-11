"""
Test autocfunction directive
"""
from textwrap import dedent

import pytest

from sphinx.ext.autodoc.directive import AutodocDirective


class TestAutoCFunction:
    """
    Testing class for the autocfunction directive

    .. note:: Parens are missing in the signature for astext(), but they show up in
        html output.
    """

    single_line_comment = """\
        void single_line_function_comment(void)
        A Single line function comment"""

    return_value_function = """\
        int return_value_function(void)
        Function with a return value"""

    multiple_parameters = """\
        int multiple_parameters(int a, int b)
        Function with multiple parameters"""

    # Note this doesn't look as nice as it will in actual HTML but you can get
    # an idea of the parameters and returns sections
    sphinx_documented_parameters = """\
        char *sphinx_documented_parameters(int param1, int param2)
        Function with sphinx documented parameters
        Parameters
        param1 -- The first parameter which is on multiple lines
        with this being the second line.
        param2 -- An alternative second parameter
        Returns
        Some return value."""

    # The clang/doxygen parsing removes newlines but keeps the indentation
    # spaces. This should be collapsed in html output.
    doxy_documented_parameters = """\
        char *doxy_documented_parameters(int param1, int param2)
        Function with doxygen style documented parameters
        Parameters
        param1 -- The first parameter which is on multiple lines      with this being the second line.
        param2 -- An alternative second parameter
        Returns
        Some return value."""

    doxy_documented_parameters_no_returns = """\
        void doxy_documented_parameters_no_returns(int water, int air)
        Doxygen style function
        This function has no returns section, but has a discussion section as described by clang.
        In Fact this has multiple discussion paragraphs.
        Parameters
        water -- An element
        air -- A different element"""

    undocumented_function = """\
        int undocumented_function(float baz)
        """
    function_with_comment_in_parameter = """\
        void *function_with_comment_in_parameter(const unknown_type *my_char_ptr)
        A function with comment inside of parameter declaration.
        Parameters
        my_char_ptr -- Pointer to my character, probably actually an array
        or string like representation."""

    function_with_array_parameters = """\
        void *function_with_array_parameters(const int array_1[34][10], unknown_type array_2[], char array_3[][20])
        A function with array parameters"""

    doc_data = [
        ("functions.c::single_line_function_comment", single_line_comment),
        ("functions.c::return_value_function", return_value_function),
        ("functions.c::multiple_parameters", multiple_parameters),
        ("functions.c::sphinx_documented_parameters", sphinx_documented_parameters),
        ("functions.c::doxy_documented_parameters", doxy_documented_parameters),
        (
            "functions.c::doxy_documented_parameters_no_returns",
            doxy_documented_parameters_no_returns,
        ),
        ("functions.c::undocumented_function", undocumented_function),
        (
            "functions.c::function_with_comment_in_parameter",
            function_with_comment_in_parameter,
        ),
        ("functions.c::function_with_array_parameters", function_with_array_parameters),
    ]

    @pytest.mark.parametrize("function, expected_doc", doc_data)
    def test_doc(self, function, expected_doc, sphinx_state):
        """
        Tests the restructured text output returned by the directive.
        """
        directive = AutodocDirective(
            "autocfunction",
            [function],
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

    def test_multiple_paragraph_doxgyen_comment(self, sphinx_state):
        """
        Tests that when processing a multi paragraph doxygen comment that the
        multiple paragraphs are preserved.
        """
        directive = AutodocDirective(
            "autocfunction",
            ["functions.c::doxy_documented_parameters_no_returns"],
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

        # first item is the function signature
        paragraphs = body.children[1]

        # 3 paragraphs from the description, and then one more child for the
        # parameter listing
        assert 4 == len(paragraphs)

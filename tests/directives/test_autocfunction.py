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
    expected_function = """\
        void my_func
        This is a function comment"""

    single_line_comment = """\
            void single_line_function_comment
            A Single line function comment"""

    return_value_function = """\
            int return_value_function
            Function with a return value"""

    multiple_parameters = """\
            int multiple_parametersint a, int b
            Function with multiple parameters"""

    # Note this doesn't look as nice as it will in actual HTML but you can get
    # an idea of the parameters and returns sections
    sphinx_documented_parameters = """\
            char *sphinx_documented_parametersint param1, int param2
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
            char *doxy_documented_parametersint param1, int param2
            Function with doxygen style documented parameters
            Parameters
            param1 -- The first parameter which is on multiple lines      with this being the second line.
            param2 -- An alternative second parameter
            Returns
            Some return value."""

    # Currently Don't know why the \xa0 are comming back in the output. Looking
    # through the debugger it appears that the xml comments from clang have
    # standard spaces, guessing it's something with the html generation from
    # sphinx
    doxy_documented_parameters_no_returns = """\
        void doxy_documented_parameters_no_returnsint\xa0water, int\xa0air
        Doxygen style function
        This function has no returns section, but has a discussion section as described by clang.
        In Fact this has multiple discussion paragraphs.
        Parameters
        water -- An element
        air -- A different element"""

    undocumented_function = """\
        undocumented_function
        """
    doc_data = [
        ('example.c::my_func', expected_function),
        ('functions.c::single_line_function_comment', single_line_comment),
        ('functions.c::return_value_function', return_value_function),
        ('functions.c::multiple_parameters', multiple_parameters),
        ('functions.c::sphinx_documented_parameters', sphinx_documented_parameters),
        ('functions.c::doxy_documented_parameters', doxy_documented_parameters),
        ('functions.c::doxy_documented_parameters_no_returns', doxy_documented_parameters_no_returns),
        # This doesn't work right now, may need to fall back to parsing with clang.
        # ('functions.c::undocumented_function', undocumented_function),
    ]

    @pytest.mark.parametrize('function, expected_doc', doc_data)
    def test_doc(self, function, expected_doc, sphinx_state):
        """
        Tests the restructured text output returned by the directive.
        """
        directive = AutodocDirective('autocfunction', [function],
                                     {'members': None}, None, None, None,
                                     None, sphinx_state, None)
        output = directive.run()

        # First item is the index entry
        assert 2 == len(output)
        body = output[1]

        # For whatever reason the as text comes back with double spacing, so we
        # knock it down to single spacing to make the expected string smaller.
        assert dedent(expected_doc) == body.astext().replace('\n\n', '\n')

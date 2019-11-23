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
        void my_funcvoid
        This is a function comment"""

    single_line_comment = """\
            void single_line_function_commentvoid
            A Single line function comment"""

    return_value_function = """\
            int return_value_functionvoid
            Function with a return value"""

    multiple_parameters = """\
            int multiple_parametersint a, int b
            Function with multiple parameters"""

    # Note this doesn't look as nice as it will in actual HTML but you can get
    # an idea of the parameters and returns sections
    documented_parameters = """\
            char * documented_parametersint param1, int param2
            Function with documented parameters
            Parameters
            param1 -- The first parameter which is on multiple lines
            with this being the second line.
            param2 -- An alternative second parameter
            Returns
            Some return value."""


    doc_data = [
        ('example.c::my_func', expected_function),
        ('functions.c::single_line_function_comment', single_line_comment),
        ('functions.c::return_value_function', return_value_function),
        ('functions.c::multiple_parameters', multiple_parameters),
        ('functions.c::documented_parameters', documented_parameters),
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

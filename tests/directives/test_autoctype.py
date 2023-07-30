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

    # This will have the title and a newline, but no content as it didn't exist
    undocumented = """\
        typedef char undocumented
        """

    # Similar to the unknown members of the union clang just falls back to
    # int's
    function_type = """\
        typedef int (unknown_return_type)
        A function type with unknown return type. This will for the generic parsing
        to happen instead of the clang soup"""

    # Similar to the unknown members of the union clang just falls back to
    # int's
    function_pointer_type = """\
        int (int *what)
        A function pointer type with unknown return type"""

    wrapped_function_pointer = """\
        typedef int (*wrapped_function_pointer)(const int*, const float)
        A function pointer wrapped on multiple lines."""

    char_array = """\
        typedef char char_array[10]
        A char array typedef"""

    typedefed_struct = """\
        typedef intermediate_type typedefed_struct
        A typedef of a struct after the fact."""

    doc_data = [
        ("types.c::my_int", my_int),
        ("types.c::undocumented", undocumented),
        ("types.c::unknown_return_type", function_type),
        ("types.c::what", function_pointer_type),
        ("types.c::wrapped_function_pointer", wrapped_function_pointer),
        ("types.c::char_array", char_array),
        ("types.c::typedefed_struct", typedefed_struct),
    ]

    @pytest.mark.parametrize("type_, expected_doc", doc_data)
    def test_doc(self, type_, expected_doc, sphinx_state):
        """
        Tests the restructured text output returned by the directive.
        """
        directive = AutodocDirective(
            "autoctype",
            [type_],
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

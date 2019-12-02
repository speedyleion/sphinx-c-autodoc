"""
Test the parsing of c enum objects
"""
from textwrap import dedent

import pytest

from sphinx.ext.autodoc.directive import AutodocDirective

class TestAutoCMacro:
    """
    Testing class for the autoctype directive for use in enums
    """
    some_enum = """\
        enum some_enum
        Enumerations are considered macros. If you want to documente them with
        napoleon then you use the section title Enumerations:.

        THE_FIRST_ENUM
        Used for the first item
        Documentation in a comment for THE_FIRST_ITEM, note this is trailing for some reason clang will apply leading comments to all the enumerations

        THE_SECOND_ENUM
        Second verse same as the first.

        THE_THIRD_ENUM
        Not once, note twice, but thrice.

        THE_LAST_ENUM
        Just to be sure."""

    doc_data = [
        ('example.c::some_enum', some_enum),
    ]

    @pytest.mark.parametrize('enum, expected_doc', doc_data)
    def test_doc(self, enum, expected_doc, sphinx_state):
        """
        Tests the restructured text output returned by the directive.
        """
        directive = AutodocDirective('autoctype', [enum], {'members': None},
                                     None, None, None, None, sphinx_state, None)
        output = directive.run()

        # First item is the index entry
        assert 2 == len(output)
        body = output[1]

        # For whatever reason the as text comes back with double spacing, so we
        # knock it down to single spacing to make the expected string smaller.
        assert dedent(expected_doc) == body.astext().replace('\n\n', '\n')

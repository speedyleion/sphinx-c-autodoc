"""
Test the napoleon extension provided by this package.
"""
from textwrap import dedent

import pytest

from sphinx.ext.autodoc.directive import AutodocDirective

from sphinx_c_autodoc.napoleon import CAutoDocString


class CustomNapoleonDocString(CAutoDocString):
    def __init__(
        self,
        docstring,
        config=None,
        app=None,
        what="",
        name="",
        obj=None,
        options=None,
    ):
        self._sections = {
            "the nonexistent section": self._parse_parameters_section,
        }
        super().__init__(docstring, config, app, what, name, obj, options)


def process_autodoc_docstring(
    app,
    what,
    name,
    obj,
    options,
    lines,
):
    """
    Call back for autodoc's ``autodoc-process-docstring`` event.
    """
    docstring = CustomNapoleonDocString(
        lines, app.config, app, what, name, obj, options
    )
    result_lines = docstring.lines()
    lines[:] = result_lines[:]


class TestNapoleonSections:
    """
    Test the new custom napoleon sections
    """

    napoleon_documented_function = """\
        int napoleon_documented_function(int yes, int another_one)
        One can also use Goolge style docstrings with napoleon for documenting
        functions.
        Functions do not support mixing doxygen style and napoleon
        style documentation.
        Parameters
        yes -- A progressive rock band from the 70s.
        another_one -- Yet one more parameter for this function.
        Returns
        The square root of 4, always."""

    members_documented_with_napoleon = """\
        struct members_documented_with_napoleon
        This example structure uses the Members: section and lets napoleon format
        the members.

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

    some_enum = """\
        enum some_enum
        If you want to document the enumerators with napoleon
        then you use the section title Enumerators:.

        enumerator THE_FIRST_ENUM
        Used for the first item
        Documentation in a comment for THE_FIRST_ITEM. Note this is trailing, for some reason clang will apply leading comments to all the enumerators

        enumerator THE_SECOND_ENUM
        Second verse same as the first.

        enumerator THE_THIRD_ENUM
        Not once, note twice, but thrice.

        enumerator THE_LAST_ENUM
        Just to be sure."""

    doc_data = [
        (
            "example.c::napoleon_documented_function",
            "function",
            napoleon_documented_function,
        ),
        (
            "example.c::members_documented_with_napoleon",
            "struct",
            members_documented_with_napoleon,
        ),
        ("example.c::some_enum", "enum", some_enum),
    ]

    @pytest.mark.parametrize("item, type_, expected_doc", doc_data)
    def test_doc(self, item, type_, expected_doc, sphinx_state):
        """
        Tests the restructured text output returned by the directive.
        """
        directive = AutodocDirective(
            f"autoc{type_}",
            [item],
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

    def test_custom_napoleon_section(self, sphinx_state):
        """
        Tests the restructured text output returned by the directive.
        """
        custom_napoleon_section = """\
            void *custom_napoleon_section(char first_param, int second_param)
            A function using a custom napoleon section that doesn't exist in this
            package.
            Parameters
            first_param -- A parameter to document
            second_param -- Why not"""

        sphinx_state.env.app.connect(
            "autodoc-process-docstring", process_autodoc_docstring
        )
        directive = AutodocDirective(
            "autocfunction",
            ["functions.c::custom_napoleon_section"],
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
        assert body.astext().replace("\n\n", "\n") == dedent(custom_napoleon_section)

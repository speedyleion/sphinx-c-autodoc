import pytest

from textwrap import dedent
from sphinx_c_autodoc import CTypeDocumenter
from docutils.statemachine import ViewList, StringList

MACRO_ONE = """\
    .. c:macro:: MY_MACRO

        The contents of this macro."""

MACRO_TWO = """\
    .. c:macro:: MY_MACRO

        The documentation of the second instance of the macro.

        This one is already multi-paragraph."""

MACRO_WITH_MODULE = """\
    .. c:macro:: MY_MACRO
        :module: some/path/to/a/file.c

        A documentation of a macro with the module syntax."""


ONE_TWO = """\
    .. c:macro:: MY_MACRO

        The contents of this macro.

        The documentation of the second instance of the macro.

        This one is already multi-paragraph."""

MODULE_ONE_TWO = """\
    .. c:macro:: MY_MACRO
        :module: some/path/to/a/file.c

        A documentation of a macro with the module syntax.

        The contents of this macro.

        The documentation of the second instance of the macro.

        This one is already multi-paragraph."""


ONE_MODULE_TWO = """\
    .. c:macro:: MY_MACRO
        :module: some/path/to/a/file.c

        The contents of this macro.

        A documentation of a macro with the module syntax.

        The documentation of the second instance of the macro.

        This one is already multi-paragraph."""

directive_data = [
    ([MACRO_ONE, MACRO_TWO], ONE_TWO),
    ([MACRO_WITH_MODULE, MACRO_ONE, MACRO_TWO], MODULE_ONE_TWO),
    ([MACRO_ONE, MACRO_WITH_MODULE, MACRO_TWO], ONE_MODULE_TWO),
]


@pytest.mark.parametrize("directives, merged_directive", directive_data)
def test_merge_directives(directives, merged_directive, documenter_bridge):
    documenter = CTypeDocumenter(documenter_bridge, "my_name")

    directive_list = [
        StringList(initlist=dedent(d).splitlines(), source="testing")
        for d in directives
    ]
    merged_output = documenter._merge_directives(directive_list)
    expected = StringList(
        initlist=dedent(merged_directive).splitlines(), source="testing"
    )
    assert merged_output.data == expected.data

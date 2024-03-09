"""
Test the usage of the compilation database
"""

import json
import os

from textwrap import dedent

import pytest

from sphinx.ext.autodoc.directive import AutodocDirective

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
compile_commands = [
    {
        "directory": ROOT_DIR,
        "command": "some_compiler -DSOME_DEFINE=1 compilation_flags_1.c",
        "file": os.path.join(ROOT_DIR, "c_source", "compilation_flags_1.c"),
    },
    {
        "directory": ROOT_DIR,
        "command": "some_compiler -Iinclude compilation_flags_2.c",
        "file": os.path.join(ROOT_DIR, "c_source", "compilation_flags_2.c"),
    },
]


class TestCompilerFlags:
    """
    Testing use of compiler flags via compilation database or directly passed args.
    """

    no_define = """\
        A file which has 2 different define paths based on SOME_DEFINE

        some_type foo(int a, int b)

        This is a version of foo that is normally available from this module"""

    define = """\
        A file which has 2 different define paths based on SOME_DEFINE

        some_type foo(int a)

        This is a version of foo which is only available when the define
        SOME_DEFINE is available."""

    no_include = """\
        A file which shows how an include made available via compilation flags
        can fully resolve a function.

        some_type foo(int a)

        When the include is not found this will return some_type."""

    include = """\
        A file which shows how an include made available via compilation flags
        can fully resolve a function.

        float foo(int a)

        When the include is found this will return a float instead of some_type."""

    doc_data = [
        ("compilation_flags_1.c", define),
        ("compilation_flags_2.c", include),
    ]

    @pytest.mark.parametrize("file_, expected_doc", doc_data)
    def test_use_compilation_database(
        self, file_, expected_doc, sphinx_state, tmp_path
    ):
        """
        Tests the restructured text output returned by the directive.
        """
        compilation_db = tmp_path / "compile_commands.json"
        compilation_db.write_text(json.dumps(compile_commands))
        sphinx_state.env.config.c_autodoc_compilation_database = str(compilation_db)
        directive = AutodocDirective(
            "autocmodule",
            [file_],
            {"members": None},
            None,
            None,
            None,
            None,
            sphinx_state,
            sphinx_state.state_machine,
        )
        output = self.get_directive_output(directive)
        assert output == dedent(expected_doc)

        assert "" == sphinx_state.env.app._warning.getvalue()

    @pytest.mark.parametrize("file_, expected_doc", doc_data)
    def test_use_compilation_args(self, file_, expected_doc, sphinx_state, tmp_path):
        include_path = os.path.join(ROOT_DIR, "include")
        sphinx_state.env.config.c_autodoc_compilation_args = [
            "-DSOME_DEFINE=1",
            f"-I{include_path}",
        ]
        directive = AutodocDirective(
            "autocmodule",
            [file_],
            {"members": None},
            None,
            None,
            None,
            None,
            sphinx_state,
            sphinx_state.state_machine,
        )
        output = self.get_directive_output(directive)
        assert output == dedent(expected_doc)

        assert "" == sphinx_state.env.app._warning.getvalue()

    mixed_comp_db_and_args = [
        ("compilation_flags_1.c", no_define),
        ("compilation_flags_2.c", include),
    ]

    @pytest.mark.parametrize("file_, expected_doc", mixed_comp_db_and_args)
    def test_compilation_args_after_compilation_database(
        self, file_, expected_doc, sphinx_state, tmp_path
    ):
        compilation_db = tmp_path / "compile_commands.json"
        compilation_db.write_text(json.dumps(compile_commands))
        sphinx_state.env.config.c_autodoc_compilation_database = str(compilation_db)
        sphinx_state.env.config.c_autodoc_compilation_args = ["-USOME_DEFINE"]
        directive = AutodocDirective(
            "autocmodule",
            [file_],
            {"members": None},
            None,
            None,
            None,
            None,
            sphinx_state,
            sphinx_state.state_machine,
        )
        output = self.get_directive_output(directive)
        assert output == dedent(expected_doc)

        assert "" == sphinx_state.env.app._warning.getvalue()

    no_compiler_flags_data = [
        ("compilation_flags_1.c", no_define),
        ("compilation_flags_2.c", no_include),
    ]

    @pytest.mark.parametrize("file_, expected_doc", no_compiler_flags_data)
    def test_file_not_found_in_compilation_database(
        self, file_, expected_doc, sphinx_state, tmp_path
    ):
        compilation_db = tmp_path / "compile_commands.json"
        compilation_db.write_text(json.dumps([]))
        sphinx_state.env.config.c_autodoc_compilation_database = str(compilation_db)
        directive = AutodocDirective(
            "autocmodule",
            [file_],
            {"members": None},
            None,
            None,
            None,
            None,
            sphinx_state,
            sphinx_state.state_machine,
        )
        output = self.get_directive_output(directive)
        assert output == dedent(expected_doc)
        assert "" == sphinx_state.env.app._warning.getvalue()

    @pytest.mark.parametrize("file_, expected_doc", no_compiler_flags_data)
    def test_no_compilation_database(self, file_, expected_doc, sphinx_state):
        """
        Tests the restructured text output returned by the directive.
        """
        directive = AutodocDirective(
            "autocmodule",
            [file_],
            {"members": None},
            None,
            None,
            None,
            None,
            sphinx_state,
            sphinx_state.state_machine,
        )
        output = self.get_directive_output(directive)
        assert output == dedent(expected_doc)
        assert "" == sphinx_state.env.app._warning.getvalue()

    @pytest.mark.parametrize("file_, expected_doc", no_compiler_flags_data)
    def test_non_existent_compilation_database(
        self, file_, expected_doc, sphinx_state, tmp_path
    ):
        compilation_db = tmp_path / "compile_commands.json"
        sphinx_state.env.config.c_autodoc_compilation_database = str(compilation_db)
        directive = AutodocDirective(
            "autocmodule",
            [file_],
            {"members": None},
            None,
            None,
            None,
            None,
            sphinx_state,
            sphinx_state.state_machine,
        )
        output = self.get_directive_output(directive)
        assert output == dedent(expected_doc)

        warnings = sphinx_state.env.app._warning.getvalue()

        db_name = str(compilation_db)
        message = f'Compilation database "{db_name}" not found.'
        assert message in warnings

    @staticmethod
    def get_directive_output(directive):
        """
        Get the textual output from running the `directive`.

        directive (AutoCDirective): The directive to get the simple text for.

        Returns:
            str: The simple text from running `directive`.
        """
        output = directive.run()

        #  1. Module paragraph
        #  2. Index entry for function
        #  3. Function paragraph
        #  4. Index entry for next function
        #  5. Function paragraph
        #  ...
        docs = (o.astext() for o in output[::1])

        body = "\n".join(docs)
        return body

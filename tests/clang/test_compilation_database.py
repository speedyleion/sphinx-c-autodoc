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
        "command": "some_compiler -DSOME_DEFINE=1 compilation_database_1.c",
        "file": os.path.join(ROOT_DIR, "c_source", "compilation_database_1.c"),
    },
    {
        "directory": ROOT_DIR,
        "command": "some_compiler -Iinclude compilation_database_2.c",
        "file": os.path.join(ROOT_DIR, "c_source", "compilation_database_2.c"),
    },
]


class TestCompilationDatabase:
    """
    Testing use of compilation database.
    """

    compilation_db_no_define = """\
        A file which has 2 different define paths based on SOME_DEFINE
        
        some_type foo(int a, int b)
        
        This is a version of foo that is normally available from this module"""

    compilation_db_define = """\
        A file which has 2 different define paths based on SOME_DEFINE
        
        some_type foo(int a)
        
        This is a version of foo which is only available when the define
        SOME_DEFINE is available."""

    compilation_db_no_include = """\
        A file which shows how an include made available via a compilation database
        can fully resolve a function.
    
        some_type foo(int a)
        
        When the include is not found this will return some_type."""

    compilation_db_include = """\
        A file which shows how an include made available via a compilation database
        can fully resolve a function.
    
        float foo(int a)
        
        When the include is found this will return a float instead of some_type."""

    doc_data = [
        ("compilation_database_1.c", compilation_db_define),
        ("compilation_database_2.c", compilation_db_include),
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
            None,
        )
        output = self.get_directive_output(directive)
        assert output == dedent(expected_doc)

        assert "" == sphinx_state.env.app._warning.getvalue()

    no_db_data = [
        ("compilation_database_1.c", compilation_db_no_define),
        ("compilation_database_2.c", compilation_db_no_include),
    ]

    @pytest.mark.parametrize("file_, expected_doc", no_db_data)
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
            None,
        )
        output = self.get_directive_output(directive)
        assert output == dedent(expected_doc)
        assert "" == sphinx_state.env.app._warning.getvalue()

    @pytest.mark.parametrize("file_, expected_doc", no_db_data)
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
            None,
        )
        output = self.get_directive_output(directive)
        assert output == dedent(expected_doc)
        assert "" == sphinx_state.env.app._warning.getvalue()

    @pytest.mark.parametrize("file_, expected_doc", no_db_data)
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
            None,
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

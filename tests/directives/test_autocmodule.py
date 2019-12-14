"""
Test autocmodule directive
"""
import logging

from textwrap import dedent

import pytest

from sphinx.ext.autodoc.directive import AutodocDirective


class TestAutoCModule:
    """
    Testing class for the autocmodule directive
    """
    module_c = """\
        This is a file comment

        void my_func

        This is a function comment"""

    file_with_only_comment = """\
        This is an empty file with only a comment.  Maybe someone needs a
        configuration header and nothing is in it..."""

    empty_file = ""

    # The extra blank lines will get squashed down in the final HTML output
    no_leading_comment = """\

        typedef int some_undocumented_type



        typedef float documented_type

        This type is documented"""

    no_file_comment = """\

        typedef char some_type

        Description of type"""

    doc_data = [
        ('module.c', module_c),
        ('no_file_comment.c', no_file_comment),
        ('file_with_only_comment.c', file_with_only_comment),
        ('empty_file.c', empty_file),
        ('no_leading_comment.c', no_leading_comment),
    ]

    @pytest.mark.parametrize('file_, expected_doc', doc_data)
    def test_doc(self, file_, expected_doc, sphinx_state):
        """
        Tests the restructured text output returned by the directive.
        """
        directive = AutodocDirective('autocmodule', [file_],
                                     {'members': None}, None, None, None,
                                     None, sphinx_state, None)
        assert dedent(expected_doc) == self.get_directive_output(directive)

    def test_fail_module_load(self, sphinx_state):
        """
        Test that a warning is raised when unable to find the module to
        document
        """
        directive = AutodocDirective('autocmodule', ['non_existent.c'],
                                     {'members': None}, None, 10, None,
                                     None, sphinx_state, None)

        output = directive.run()
        assert output == []

        warnings = sphinx_state.env.app._warning.getvalue()

        messages = ('Unable to find', 'non_existent.c')
        for message in messages:
            assert message in warnings

    def test_no_members_option(self, sphinx_state):
        """
        Test that when no members is provided that the members don't get
        documented.
        """
        just_file_doc = """\
            This is a file comment"""

        directive = AutodocDirective('autocmodule', ['module.c'],
                                     {}, None, None, None,
                                     None, sphinx_state, None)

        assert dedent(just_file_doc) == self.get_directive_output(directive)

    def test_members_called_out(self, sphinx_state):
        """
        Test that when specific members are called out, only those members
        show in documentation.
        """
        example_c = """\
            This is a file comment. The first comment in the file will be grabbed.
            Often times people put the copyright in these. If that is the case then you
            may want to utilize the pre processing hook, c-autodoc-pre-process.
            One may notice that this comment block has a string of *** along the top
            and the bottom. For the file comment these will get stripped out, however for
            comments on other c constructs like macros, functions, etc. clang is often
            utilized and it does not understand this pattern, so the
            c-autodoc-pre-process hook may be something to use to sanitize these kind
            of comments.

            TOO_SIMPLE

            A simple macro definition

            int some_flag_variable

            File level variables can also be documented"""

        directive = AutodocDirective('autocmodule', ['example.c'],
                                     {'members': 'TOO_SIMPLE, some_flag_variable'},
                                     None, None, None, None, sphinx_state, None)

        assert dedent(example_c) == self.get_directive_output(directive)

    def test_non_existent_member_causes_warning(self, sphinx_state):
        """
        Test that when specific a specific member is called out and it doesn't
        exist a warning is emitted.
        """
        example_c = """\
            This is a file comment. The first comment in the file will be grabbed.
            Often times people put the copyright in these. If that is the case then you
            may want to utilize the pre processing hook, c-autodoc-pre-process.
            One may notice that this comment block has a string of *** along the top
            and the bottom. For the file comment these will get stripped out, however for
            comments on other c constructs like macros, functions, etc. clang is often
            utilized and it does not understand this pattern, so the
            c-autodoc-pre-process hook may be something to use to sanitize these kind
            of comments.

            TOO_SIMPLE

            A simple macro definition

            int some_flag_variable

            File level variables can also be documented"""

        directive = AutodocDirective('autocmodule', ['example.c'],
                                     {'members': 'TOO_SIMPLE, not_here, some_flag_variable'},
                                     None, None, None, None, sphinx_state, None)

        assert dedent(example_c) == self.get_directive_output(directive)

        warnings = sphinx_state.env.app._warning.getvalue()

        messages = ("Missing member \"not_here\"",)
        for message in messages:
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

        body = '\n'.join(docs)
        return body

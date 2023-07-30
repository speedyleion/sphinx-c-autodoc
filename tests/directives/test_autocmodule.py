"""
Test autocmodule directive
"""
from textwrap import dedent

import pytest

from sphinx.ext.autodoc.directive import AutodocDirective


class TestAutoCModule:
    """
    Testing class for the autocmodule directive
    """

    module_c = """\
        This is a file comment

        void my_func(void)

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

    file_with_private_members = """\

        PRIVATE_MACRO

        Defines in C files are inherently private.

        PRIVATE_FUNCTION_MACRO(_a, _b)

        Function macros in C files should also be private

        typedef int foo

        Types, in c files are inherently private.

        static int my_var

        static variables are inherently private

        float a_public_var

        Non static variables are not private

        enum private_enum

        Enums in c files are inherently private



        enumerator ENUM_1



        struct private_struct

        structures in c files are inherently private



        int a



        void function1(int a)

        Non static functions are not private

        static void function2(int a)

        static functions, in c files are inherently private."""

    doc_data = [
        ("module.c", module_c),
        ("no_file_comment.c", no_file_comment),
        ("file_with_only_comment.c", file_with_only_comment),
        ("empty_file.c", empty_file),
        ("no_leading_comment.c", no_leading_comment),
        ("nested/module.c", module_c),
        ("file_with_private_members.c", file_with_private_members),
    ]

    @pytest.mark.parametrize("file_, expected_doc", doc_data)
    def test_doc(self, file_, expected_doc, sphinx_state):
        """
        Tests the restructured text output returned by the directive.
        """
        directive = AutodocDirective(
            "autocmodule",
            [file_],
            {"members": None, "private-members": True, "member-order": "bysource"},
            None,
            None,
            None,
            None,
            sphinx_state,
            sphinx_state.state_machine,
        )
        assert self.get_directive_output(directive) == dedent(expected_doc)

    def test_fail_module_load(self, sphinx_state):
        """
        Test that a warning is raised when unable to find the module to
        document
        """
        directive = AutodocDirective(
            "autocmodule",
            ["non_existent.c"],
            {"members": None},
            None,
            10,
            None,
            None,
            sphinx_state,
            sphinx_state.state_machine,
        )

        output = directive.run()
        assert output == []

        warnings = sphinx_state.env.app._warning.getvalue()

        messages = ("Unable to find", "non_existent.c")
        for message in messages:
            assert message in warnings

    def test_no_members_option(self, sphinx_state):
        """
        Test that when no members is provided that the members don't get
        documented.
        """
        just_file_doc = """\
            This is a file comment"""

        directive = AutodocDirective(
            "autocmodule",
            ["module.c"],
            {},
            None,
            None,
            None,
            None,
            sphinx_state,
            sphinx_state.state_machine,
        )

        assert self.get_directive_output(directive) == dedent(just_file_doc)

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

        directive = AutodocDirective(
            "autocmodule",
            ["example.c"],
            {"members": "TOO_SIMPLE, some_flag_variable"},
            None,
            None,
            None,
            None,
            sphinx_state,
            sphinx_state.state_machine,
        )

        assert self.get_directive_output(directive) == dedent(example_c)

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

        directive = AutodocDirective(
            "autocmodule",
            ["example.c"],
            {"members": "TOO_SIMPLE, not_here, some_flag_variable"},
            None,
            None,
            None,
            None,
            sphinx_state,
            sphinx_state.state_machine,
        )

        assert self.get_directive_output(directive) == dedent(example_c)

        warnings = sphinx_state.env.app._warning.getvalue()

        messages = ('Missing member "not_here"',)
        for message in messages:
            assert message in warnings

    def test_no_private_members_option(self, sphinx_state):
        file_with_no_private_members = """\

            float a_public_var

            Non static variables are not private

            void function1(int a)

            Non static functions are not private"""

        directive = AutodocDirective(
            "autocmodule",
            ["file_with_private_members.c"],
            {"members": None, "no-private-members": None},
            None,
            None,
            None,
            None,
            sphinx_state,
            sphinx_state.state_machine,
        )

        output = self.get_directive_output(directive)
        assert output == dedent(file_with_no_private_members)

    def test_no_private_members_on_header_file(self, sphinx_state):
        header_with_no_private_members = """\

            typedef float header_type

            This should always be visible, even if no-private-members is in use."""

        directive = AutodocDirective(
            "autocmodule",
            ["header_with_types.h"],
            {"members": None, "no-private-members": None},
            None,
            None,
            None,
            None,
            sphinx_state,
            sphinx_state.state_machine,
        )

        output = self.get_directive_output(directive)
        assert output == dedent(header_with_no_private_members)

    def test_no_undoc_members(self, sphinx_state):
        header_with_undocumented_members = """\
            This header file as some undocumented contents

            struct struct_with_undocumented_member

            The structure member bar is undocumented.  It will still show in the
            documentation, only file level constructs will be filtered with this
            option.



            int bar

            """

        directive = AutodocDirective(
            "autocmodule",
            ["header_with_undocumented_members.h"],
            {"members": None, "no-undoc-members": None},
            None,
            None,
            None,
            None,
            sphinx_state,
            sphinx_state.state_machine,
        )

        output = self.get_directive_output(directive)
        assert output == dedent(header_with_undocumented_members)

    def test_undoc_members_specified(self, sphinx_state):
        header_with_undocumented_members = """\
            This header file as some undocumented contents

            _MY_HEADER_GUARD



            struct struct_with_undocumented_member

            The structure member bar is undocumented.  It will still show in the
            documentation, only file level constructs will be filtered with this
            option.



            int bar



            struct undocumented_struct



            int foo





            float what

            """

        directive = AutodocDirective(
            "autocmodule",
            ["header_with_undocumented_members.h"],
            # Note: The undoc-members option is actually in the common conf.py
            # file.  And it is an autodoc specific feature, this just tests
            # that the extension obeys that.
            {"members": None},
            None,
            None,
            None,
            None,
            sphinx_state,
            sphinx_state.state_machine,
        )

        output = self.get_directive_output(directive)
        assert output == dedent(header_with_undocumented_members)

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

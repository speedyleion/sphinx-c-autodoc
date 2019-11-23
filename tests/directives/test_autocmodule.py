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
    expected_example_c = """\
        This is a file comment

        void my_funcvoid

        This is a function comment"""

    types_c = """\

        my_int

        This is basic typedef from a native type to another name.

        my_struct_type

        A struct that is actually anonymouse but is typedefed in place.

        some_struct

        A plain struct that is not typedefed.

        typedefed_struct

        A typedef of a struct after the fact.

        undocumented

        """

    file_with_only_comment = """\
        This is an empty file with only a comment.  Maybe someone needs a
        configuration header and nothing is in it..."""

    empty_file = ""

    # The extra blank lines will get squashed down in the final HTML output
    no_leading_comment = """\

        some_undocumented_type



        documented_type

        This type is documented"""

    doc_data = [
        ('example.c', expected_example_c),
        ('types.c', types_c),
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
        output = directive.run()

        #  1. Module paragraph
        #  2. Index entry for function
        #  3. Function paragraph
        #  4. Index entry for next function
        #  5. Function paragraph
        #  ...
        docs = (o.astext() for o in output[::1])

        body = '\n'.join(docs)

        assert dedent(expected_doc) == body

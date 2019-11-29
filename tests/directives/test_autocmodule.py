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

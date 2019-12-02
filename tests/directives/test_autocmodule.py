"""
Test autocmodule directive
"""
import logging

from textwrap import dedent

import pytest

from sphinx.ext.autodoc.directive import AutodocDirective

@pytest.fixture()
def local_capsys(capsys):
    """
    A modified version of capsys.

    This original author is lacking sufficient knowledge at this time to
    properly mix capsys and another fixture, so this less than ideal work
    around exists.

    It appears that capsys will open and close through each state of the test
    run; setup, run, and teardown.

    What happens is during setup, capsys sets up the sys.stderr to go to an
    IO stream. The second fixture, `sphinx_state`, will set up its error
    handling to use `sys.stderr` which is properly routed to capsys.
    The setup finishes and capsys closes the IO stream and re-instates
    sys.stderr.

    The main test run starts and capsys again captures sys.stderr, however
    the `sphinx_state` from before is pointing to the original mapping capsys
    had done, which is closed and causes an error when sphinx attempts to
    write to it.
    """

    # Setting the capture fixture to None, prevents the IO stream from being closed.
    old_fixture = capsys.request._pyfuncitem._capture_fixture
    capsys.request._pyfuncitem._capture_fixture = None

    yield capsys

    # manually close the old fixture
    old_fixture.close()


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

    def test_fail_module_load(self, local_capsys, sphinx_state):
        """
        Test that a warning is raised when unable to find the module to
        document
        """
        directive = AutodocDirective('autocmodule', ['non_existent.c'],
                                     {'members': None}, None, 10, None,
                                     None, sphinx_state, None)

        output = directive.run()
        assert output == []

        captured = local_capsys.readouterr()

        messages = ('Unable to find', 'non_existent.c')
        for message in messages:
            assert message in captured.err
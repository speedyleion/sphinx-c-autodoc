"""
A test file for testing the running of sphinx directives
"""
import argparse
import pytest
import os

from textwrap import dedent

from docutils.parsers.rst.states import RSTStateMachine, Struct, Inliner, state_classes
from docutils.parsers.rst import directives
from docutils.parsers.rst.languages import en
from docutils.utils import new_document
from sphinx.testing.path import path
from sphinx.util.docutils import sphinx_domains

from sphinx.ext.autodoc.directive import AutodocDirective


pytest_plugins = 'sphinx.testing.fixtures'

@pytest.fixture()
def local_app(make_app):
    """
    Creates a sphinx app specific to this environment.

    The main thing that is set up is the path to the conf.py file.

    yields:
        SphinxApp: The sphinx app.

    """
    # Provide sphinx with the path to the documentation directory.
    conf_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))

    # Note the sphinx fixture expects a :class:`path` object, not a string
    yield make_app(srcdir=path(conf_dir))


@pytest.fixture()
def sphinx_state(local_app):
    """
    Fixture which will provide a sphinx state for use in testing sphinx
    directives.

    Yields:
        :class:`docutils.parsers.rst.states.State` A state for use in testing
            directive functionality.
    """
    # Get the environment and decorate it with what sphinx may need for the
    # parsing.
    env = local_app.env
    env.temp_data['docname'] = 'test'  # A fake document name


    # Create a document and inliner object, to be perfectly honest not sure
    # exactly what these are or do, but needed to get the directive to run.
    document = new_document(__file__)
    document.settings.pep_references = 1
    document.settings.rfc_references = 1
    document.settings.env = env
    document.settings.tab_width = 4
    inliner = Inliner()
    inliner.init_customizations(document.settings)

    # Create a state machine so that we can get a state to pass back.
    statemachine = RSTStateMachine(state_classes=state_classes, initial_state='Body')
    state = statemachine.get_state()
    state.document = document
    state.memo = Struct(inliner=inliner, language=en, title_styles=[],
                        reporter=document.reporter, document=document,
                        section_level=0, section_bubble_up_kludge=False)

    state.memo.reporter.get_source_and_line = statemachine.get_source_and_line

    # Sphinx monkeypatches docutils when run. This is how it get's
    # monkeypatched so that the python directives and roles can be found
    with sphinx_domains(env):

        # Provide the state back to the test.
        yield state

class TestAutoCModule:
    """
    Testing class for the autocmodule directive
    """
    expected_example_c = """\
        This is a file comment

        my_func
        This is a function comment"""

    doc_data = [
        ('autocmodule', ['example.c'], expected_example_c),
    ]

    @pytest.mark.parametrize('directive, args, expected_doc', doc_data)
    def test_doc(self, directive, args, expected_doc, sphinx_state):
        """
        Tests the restructured text output returned by the directive.
        """
        directive = AutodocDirective(directive, args, {'members': None}, None, None, None, None, sphinx_state, None)
        output = directive.run()

        #  1. Module paragraph
        #  2. Index entry for function
        #  3. Function paragraph
        assert 3 == len(output)

        # Triple newlines for the double knockdown below
        body = '\n\n\n'.join((output[0].astext(), output[2].astext()))

        # For whatever reason the as text comes back with double newlines, so we
        # knock it down to single spacing to make the expected string smaller.
        assert dedent(expected_doc) == body.replace('\n\n', '\n')


class TestAutoCFunction:
    """
    Testing class for the autocfunction directive
    """
    expected_function = """\
        my_func
        This is a function comment"""

    single_line_comment = """\
            single_line_function_comment
            A Single line function comment"""

    return_value_function = """\
            return_value_function
            Function with a return value"""

    multiple_parameters = """\
            multiple_parameters
            Function with multiple parameters"""

    # Note this doesn't look as nice as it will in actual HTML but you can get
    # an idea of the parameters and returns sections
    documented_parameters = """\
            documented_parameters
            Function with documented parameters
            Parameters
            param1 -- The first parameter which is on multiple lines
            with this being the second line.
            param2 -- An alternative second parameter
            Returns
            Some return value."""


    doc_data = [
        ('autocfunction', ['example.c::my_func'], expected_function),
        ('autocfunction', ['functions.c::single_line_function_comment'], single_line_comment),
        ('autocfunction', ['functions.c::return_value_function'], return_value_function),
        ('autocfunction', ['functions.c::multiple_parameters'], multiple_parameters),
        ('autocfunction', ['functions.c::documented_parameters'], documented_parameters),
    ]

    @pytest.mark.parametrize('directive, args, expected_doc', doc_data)
    def test_doc(self, directive, args, expected_doc, sphinx_state):
        """
        Tests the restructured text output returned by the directive.
        """
        directive = AutodocDirective(directive, args, {'members': None}, None, None, None, None, sphinx_state, None)
        output = directive.run()

        # First item is the index entry
        assert 2 == len(output)
        body = output[1]

        # For whatever reason the as text comes back with double spacing, so we
        # knock it down to single spacing to make the expected string smaller.
        assert dedent(expected_doc) == body.astext().replace('\n\n', '\n')


class TestAutoCType:
    """
    Testing class for the autoctype directive
    """
    my_int = """\
        my_int
        This is basic typedef from a native type to another name."""

    my_struct_type = """\
            my_struct_type
            A struct that is actually anonymouse but is typedefed in place."""

    # Note the '*' around `not` are bold attributes in html so are stripped away
    # in the as_text()
    some_struct = """\
            some_struct
            A plain struct that is not typedefed."""

    typedefed_struct = """\
            typedefed_struct
            A typedef of a struct after the fact."""

    doc_data = [
        ('autoctype', ['types.c::my_int'], my_int),
        ('autoctype', ['types.c::my_struct_type'], my_struct_type),
        ('autoctype', ['types.c::some_struct'], some_struct),
        ('autoctype', ['types.c::typedefed_struct'], typedefed_struct),
    ]

    @pytest.mark.parametrize('directive, args, expected_doc', doc_data)
    def test_doc(self, directive, args, expected_doc, sphinx_state):
        """
        Tests the restructured text output returned by the directive.
        """
        directive = AutodocDirective(directive, args, {'members': None}, None, None, None, None, sphinx_state, None)
        output = directive.run()

        # First item is the index entry
        assert 2 == len(output)
        body = output[1]

        # For whatever reason the as text comes back with double spacing, so we
        # knock it down to single spacing to make the expected string smaller.
        assert dedent(expected_doc) == body.astext().replace('\n\n', '\n')

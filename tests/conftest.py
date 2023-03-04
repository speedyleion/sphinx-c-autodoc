"""
Common pytest configuration for the test suites
"""

import os
import sys

import pytest

from docutils.parsers.rst.states import RSTStateMachine, Struct, Inliner, state_classes
from docutils.parsers.rst.languages import en
from docutils.statemachine import StringList
from docutils.utils import new_document
from sphinx.testing.path import path
from sphinx.util.docutils import sphinx_domains

# SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
# sys.path.append(os.path.join(SCRIPT_DIR, '..', 'src'))

pytest_plugins = "sphinx.testing.fixtures"


@pytest.fixture()
def local_app(make_app):
    """
    Creates a sphinx app specific to this environment.

    The main thing that is set up is the path to the conf.py file.

    yields:
        SphinxApp: The sphinx app.

    """
    # Provide sphinx with the path to the documentation directory.
    conf_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets"))

    # Note the sphinx fixture expects a :class:`path` object, not a string
    yield make_app(srcdir=path(conf_dir))


@pytest.fixture()
def sphinx_state(local_app):
    """
    Fixture which will provide a sphinx state for use in testing sphinx
    directives.

    Yields:
        :class:`docutils.parsers.rst.states.State`: A state for use in testing
            directive functionality.
    """
    # Get the environment and decorate it with what sphinx may need for the
    # parsing.
    env = local_app.env
    env.temp_data["docname"] = "test"  # A fake document name

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
    statemachine = RSTStateMachine(state_classes=state_classes, initial_state="Body")
    statemachine.input_lines = StringList([""] * 40)
    state = statemachine.get_state()
    state.document = document
    state.memo = Struct(
        inliner=inliner,
        language=en,
        title_styles=[],
        reporter=document.reporter,
        document=document,
        section_level=0,
        section_bubble_up_kludge=False,
    )

    state.memo.reporter.get_source_and_line = statemachine.get_source_and_line

    # The environemnt isn't normally available on the state in sphinx, but it's
    # done here to make testing easier.
    state.env = env

    # Sphinx monkeypatches docutils when run. This is how it get's
    # monkeypatched so that the python directives and roles can be found
    with sphinx_domains(env):
        # Provide the state back to the test.
        yield state

import pytest

from sphinx.ext.autodoc.directive import DocumenterBridge
from docutils.parsers.rst.states import Struct


@pytest.fixture()
def documenter_bridge(sphinx_state):
    """
    Common documenter bridge used for creating directives. This only provides
    what's been deemed necessary for testing so anything extra should be
    added as needed.

    Yields:
        DocumenterBridge for creating documenters.
    """
    yield DocumenterBridge(sphinx_state.env, None, None, None, state=sphinx_state)

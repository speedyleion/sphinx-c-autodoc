import pytest

from sphinx.ext.autodoc.directive import DocumenterBridge
from docutils.parsers.rst.states import Struct


@pytest.fixture()
def documenter_bridge():
    """
    Common documenter bridge used for creating directives. This only provides
    what's been deemed necessary for testing so anything extra should be
    added as needed.

    Yields:
        DocumenterBridge for creating documenters.
    """
    settings = Struct(tab_width=4)
    document = Struct(settings=settings)
    state = Struct(document=document)
    yield DocumenterBridge(None, None, None, None, state=state)

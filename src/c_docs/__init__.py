from sphinx.ext.autodoc import Documenter

class CFileDocumenter(Documenter):
    """
    """
    objtype = 'cfile'
    pass

def setup(app):
    """
    Setup function for registering this with sphinx
    """
    app.require_sphinx('1.8')
    app.add_autodocumenter(CFileDocumenter)

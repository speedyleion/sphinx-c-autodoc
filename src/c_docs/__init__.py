from sphinx.ext.autodoc import Documenter
from sphinx.util.docstrings import prepare_docstring
from docutils.parsers.rst import Directive
from docutils.statemachine import ViewList
from docutils import nodes
from c_docs import parser
import os

class CFileDocumenter(Documenter):
    """
    A C file autodocument class to work with 
    `autodoc https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#module-sphinx.ext.autodoc`_
    extension for sphinx.

    This auto documenter will be registered as a directive named `autocmodule`,
    there may be a way to override the python `automodule`, just not sure yet...
    """
    domain = 'c'
    objtype = 'cmodule'
    directivetype = 'module'

    # HACK for dev/testing
    file_doc = 'This is a file comment'


    def resolve_name(self, modname, parents, path, base):
        """
        Not sure yet
        Args:
            modname (str|None): Believe this is only for sub elements, i.e.
                `some_c_file::some_function`, then `some_c_file` would be
                provided.
            parents (list[]): This is for python modules of hte form
                `package.sub_dir.sub.module` the parents of `module` would be
                [`package`, `sub_dir`, `sub`].
            path (str|None): It seems that this is the unsplit version of `parents`
            base (str): Appears to be the c file name.

        Returns:
            Not sure yet..
        """
        return base, []

    def import_object(self) -> bool:
        """Parse the C file and build up the document structure.
        
        This will parse the C file and store the document structure into
        :attr:`_c_doc`
        """
        path = os.path.join(self.env.app.confdir, self.env.config.c_root)
        filename = os.path.join(path, self.get_real_modname())
        self._c_doc = parser.parse(filename)
        
        return True

    def get_real_modname(self) -> str:
        """Get the real module name of an object to document.

        It can differ from the name of the module through which the object was
        imported.
        """
        return f'{self.modname}.c'

    def get_sourcename(self) -> str:
        return f'docstring of {self.fullname}.c'


    def get_doc(self, encoding=None, ignore=1):
        """Decode and return lines of the docstring(s) for the object."""
        docstring = self.file_doc
        tab_width = self.directive.state.document.settings.tab_width
        return [prepare_docstring(docstring, ignore, tab_width)]


class CModule(Directive):
    """
    """
    has_content = True
    required_arguemnts = 1

    pass

    def run(self):
        """
        Not sure yet
        """
        state = self.state
        node = nodes.section()

        rst = ViewList(self.content, 'testing')

        # Parse the restructured text into nodes.
        state.nested_parse(rst, 0, node, match_titles=1)

        return node.children

def setup(app):
    """
    Setup function for registering this with sphinx
    """
    app.require_sphinx('1.8')
    app.add_autodocumenter(CFileDocumenter)
    app.add_directive_to_domain('c', 'module', CModule)
    app.add_config_value('c_root', '', 'env')

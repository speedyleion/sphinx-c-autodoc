from sphinx.ext.autodoc import Documenter
from docutils.parsers.rst import Directive
from docutils.statemachine import ViewList
from docutils import nodes

class CFileDocumenter(Documenter):
    """
    """
    domain = 'c'
    objtype = 'cfile'
    directivetype = 'module'

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
        """Never import anything."""
        return True

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

        rst = ViewList(['Hello What is Up?'], 'testing')

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

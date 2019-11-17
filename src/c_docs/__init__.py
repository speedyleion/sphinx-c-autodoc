from sphinx.ext.autodoc import Documenter

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


def setup(app):
    """
    Setup function for registering this with sphinx
    """
    app.require_sphinx('1.8')
    app.add_autodocumenter(CFileDocumenter)

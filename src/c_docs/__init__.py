"""
C_docs is a package which provide c source file parsing for sphinx.

It is composed of multiple directives and settings:

.. rst:directive:: .. autocmodule:: filename

    A directive which will automatically parse `filename` and create the
    documentation for it.  The `filename` is relative to the config value
    `c_root`.  This can be used for both c source files as
    well as c header files.

    This will basically in place expand into:

        .. c:module:: filename

            Any text from the *first* comment in the file, provided that the
            comment is not for some other construct.

            .. c:type:: some_struct

                .. c:member:: member_1

                    any comments about this.

            .. c:function:: some_funtion(int param_1, char param_2)

                Comment from the function header.  The function header comment
                is the closest preceding comment.

            ...


    Any and all :rst:dir:`c:function`, :rst:dir:`c:type`, etc at the
    root of `filename` will be expanded into the documentation.

.. rst:directive:: .. c:module:: filename

    A directive to document a c file.  This is similar to :rst:dir:`py:module`
    except it's for the C domain.  This can be used for both c source files as
    well as c header files.


"""
import os

from docutils.parsers.rst import Directive
from docutils.statemachine import ViewList
from docutils import nodes
from sphinx.ext.autodoc import Documenter
from sphinx.util.docstrings import prepare_docstring

from c_docs import parser


class CModuleDocumenter(Documenter):
    # pylint: disable=line-too-long
    """
    A C module autodocument class to work with
    `autodoc https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#module-sphinx.ext.autodoc`_
    extension for sphinx.

    This auto documenter will be registered as a directive named `autocmodule`,
    there may be a way to override the python `automodule`, just not sure yet...


    """
    # pylint: enable=line-too-long
    domain = 'c'
    objtype = 'cmodule'
    directivetype = 'module'

    def __init__(self, *args, **kwargs):
        self._c_doc = None
        super().__init__(*args, **kwargs)

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        """
        Not sure yet...
        """
        return True

    def resolve_name(self, modname, parents, path, base):
        """
        Not sure yet

        Args:
            modname (str): Believe this is only for sub elements, i.e.
                `some_c_file::some_function`, then `some_c_file` would be
                provided.
            parents (list): This is for python modules of hte form
                `package.sub_dir.sub.module` the parents of `module` would be
                [`package`, `sub_dir`, `sub`].
            path (str): It seems that this is the unsplit version of `parents`
            base (str): Appears to be the c file name.

        Returns:
            tuple: Not sure yet..
        """
        return path + base, []

    def import_object(self):
        """Parse the C file and build up the document structure.

        This will parse the C file and store the document structure into
        :attr:`_c_doc`
        """
        path = os.path.join(self.env.app.confdir, self.env.config.c_root)
        filename = os.path.join(path, self.get_real_modname())
        self._c_doc = parser.parse(filename)

        return True

    def get_doc(self, encoding=None, ignore=1):
        """Decode and return lines of the docstring(s) for the object."""
        docstring = '\n'.join(self._c_doc)
        tab_width = self.directive.state.document.settings.tab_width
        return [prepare_docstring(docstring, ignore, tab_width)]


class CModule(Directive):
    """
    Module directive for C files
    """
    has_content = True
    required_arguments = 1

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
    app.add_autodocumenter(CModuleDocumenter)
    app.add_directive_to_domain('c', 'module', CModule)
    app.add_config_value('c_root', '', 'env')

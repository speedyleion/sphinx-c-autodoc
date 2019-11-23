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

from typing import Any, Callable, Dict, List, Tuple

from docutils.parsers.rst import Directive, directives
from docutils.statemachine import ViewList
from docutils import nodes
from sphinx.domains import c
from sphinx.ext.autodoc import Documenter, members_option
from sphinx.util.docstrings import prepare_docstring

from clang import cindex

from c_docs import parser


class CObjectDocumenter(Documenter):
    # pylint: disable=line-too-long
    """
    A C object autodocument class to work with
    `autodoc https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#module-sphinx.ext.autodoc`_
    extension for sphinx.
    """
    # pylint: enable=line-too-long
    domain = 'c'

    # Filler type, this base class isn't used directly
    directivetype = 'object'

    # must be higher than the AttributeDocumenter, else it will steal the c
    # objects
    priority = 11

    option_spec = {
        'members': members_option,
    }  # type: Dict[str, Callable]

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        """
        Returns:
            bool: True if this class can document the `member`.
        """
        return member.type == cls.directivetype

    def resolve_name(self, modname, parents, path, base):
        """
        Resolve the module and object name of the object to document.
        This can be derived in two ways:
        - Naked: Where the argument is only the file/module name `my_file.c`
        - Double colons: Where the argument to the directive is of the form
          `my_file.c::some_func`.

        Args:
            modname (str): Only set when called with double colons.  This will
                be the left side of the double colons.
            parents (list): The list split('.') version of path.
                - The filename without the extension when naked argument is used.
                - Any parents when double colon argument is used. For example
                  structs or unions of `my_struct.member_name` would have a
                  parents entry of ['my_struct']
            path (str): Two possible states:
                - None if `parents` is the empty list.
                - The '.'.join() version of `parents`, with a trailing `.`
            base (str): The name of the object:
                - This will be the file extension when naked argument is used.
                - This will be the object, function, type, etc when double colon
                  argument is used.

        Returns:
            tuple: (str, [str]) The module name, and the object names (if any).
                The object names will be joined with a `.`.
        """
        if modname:
            return modname, parents + [base]

        return path + base, []

    def import_object(self):
        """Parse the C file and build up the document structure.

        This will parse the C file and store the document structure into
        :attr:`object`
        """
        path = os.path.join(self.env.app.confdir, self.env.config.c_root)
        filename = os.path.join(path, self.get_real_modname())
        self.module = parser.parse(filename)

        self.object = self.module
        self.object_name = self.name

        # objpath is set when double colons are used in :meth:`resolve_name`.
        # i.e. this is a node or sub-node in a module.
        if self.objpath:
            for obj in self.objpath:
                self.object_name = obj
                self.object = self.object.children[self.object_name]

        return True

    def get_doc(self, encoding=None, ignore=1):
        """Decode and return lines of the docstring(s) for the object."""
        docstring = self.object.doc
        tab_width = self.directive.state.document.settings.tab_width
        return [prepare_docstring(docstring, ignore, tab_width)]

    def get_object_members(self, want_all: bool):
        """Return `(members_check_module, members)` where `members` is a
        list of `(membername, member)` pairs of the members of *self.object*.

        If *want_all* is True, return all members.  Else, only return those
        members given by *self.options.members* (which may also be none).
        """
        return False, list(self.object.children.items())

    def filter_members(self, members: List[Tuple[str, Any]], want_all: bool
                       ) -> List[Tuple[str, Any, bool]]:
        """Filter the given member list.

        Members are skipped if

        - they are private (except if given explicitly or the private-members
          option is set)
        - they are special methods (except if given explicitly or the
          special-members option is set)
        - they are undocumented (except if the undoc-members option is set)

        The user can override the skipping decision by connecting to the
        ``autodoc-skip-member`` event.
        """
        ret = []
        isattr = False
        for (membername, member) in members:
            ret.append((membername, member, isattr))

        return ret

    def format_name(self) -> str:
        """Format the name of *self.object*.

        This normally should be something that can be parsed by the generated
        directive, but doesn't need to be (Sphinx will display it unparsed
        then).

        For things like functions and others this will include the return type.
        """
        return self.object.format_name()

    def format_args(self, **kwargs) -> str:
        """
        Creates the parenthesis version of the function signature.  i.e. this
        will be the `(int hello, int what)` portion of the header.
        """
        return self.object.format_args(**kwargs)

    def add_directive_header(self, sig: str) -> None:
        """Add the directive header and options to the generated content."""

        # save off the :attr:`objpath`, this will prevent the :module: option
        # from being populated in some directives
        objpath = self.objpath
        self.objpath = []
        super().add_directive_header(sig)
        self.objpath = objpath


class CModuleDocumenter(CObjectDocumenter):
    """
    This auto documenter will be registered as a directive named `autocmodule`,
    there may be a way to override the python `automodule`, just not sure yet...
    """
    objtype = 'cmodule'
    directivetype = 'module'

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        """
        Modules are top levels so should never be included as a child of another
        c object.

        Returns:
            bool: True if this class can document the `member`.
        """
        return False


class CTypeDocumenter(CObjectDocumenter):
    """
    The documenter for the autoctype directive.

    This handles:
        - types
        - structs
        - unions

    """
    domain = 'c'
    objtype = 'ctype'
    directivetype = 'type'

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        """
        Returns:
            bool: True if this class can document the `member`.
        """
        return member.type in ('struct', 'type', 'union')


class CMemberDocumenter(CObjectDocumenter):
    """
    The documenter for the autocmember directive.

    This handles structure and union fields.
    """
    domain = 'c'
    objtype = 'cmember'
    directivetype = 'member'


class CFunctionDocumenter(CObjectDocumenter):
    """
    The documenter for the autocfunction directive.
    """
    domain = 'c'
    objtype = 'cfunction'
    directivetype = 'function'


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
    app.setup_extension('sphinx.ext.autodoc')
    app.add_autodocumenter(CModuleDocumenter)
    app.add_autodocumenter(CFunctionDocumenter)
    app.add_autodocumenter(CTypeDocumenter)
    app.add_autodocumenter(CMemberDocumenter)
    app.add_directive_to_domain('c', 'module', CModule)
    app.add_config_value('c_root', '', 'env')

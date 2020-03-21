"""
sphinx_c_autodoc is a package which provide c source file parsing for sphinx.

It is composed of multiple directives and settings:

.. rst:directive:: .. c:module:: filename

    A directive to document a c file.  This is similar to :rst:dir:`py:module`
    except it's for the C domain.  This can be used for both c source files as
    well as c header files.


"""
import json
import os
import re

from dataclasses import dataclass, field
from itertools import groupby

from typing import Any, List, Optional, Tuple, Dict

from docutils.statemachine import ViewList, StringList
from docutils import nodes
from sphinx.domains.c import CObject
from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx.util.docstrings import prepare_docstring
from sphinx.ext.autodoc import Documenter, members_option, bool_option
from sphinx.ext.autodoc.directive import DocumenterBridge

from sphinx_c_autodoc import loader
from sphinx_c_autodoc.domains.c import patch_c_domain


# TODO not real fond of this being here in the main c autodoc file, need to
# find a way to make it easier to cache the documented files.
@dataclass
class ViewCodeListing:
    """
    A data structure used for constructing a viewcode source listing.

    Attributes:
        raw_listing:
            The plain text representation of the code. This should be
            basically the output of file.read().

        ast (Dict):
            A dictionary like representation of the code constructs.
            See :ref:`developer_notes:Common Terms`.

        doc_links (Dict): To be used by the consumers, i.e. viewcode.

    """

    raw_listing: str
    ast: Dict
    doc_links: Dict = field(default_factory=dict)


logger = logging.getLogger(__name__)


class CObjectDocumenter(Documenter):
    # pylint: disable=line-too-long
    """
    A C object autodocument class to work with
    `autodoc <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#module-sphinx.ext.autodoc>`_
    extension for sphinx.
    """
    # pylint: enable=line-too-long
    domain = "c"

    # Filler type, this base class isn't used directly
    directivetype = "object"

    # must be higher than the AttributeDocumenter, else it will steal the c
    # objects
    priority = 11

    option_spec = {"members": members_option, "noindex": bool_option}

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        """
        Parameters:
            member (object): The member item to document.  This type is specific
                to the item being processed by autodoc.  These classes will
                only attempt to process
                :class:`sphinx_c_autodoc.loader.CObjectDocumenter` members.

            membername (str): The name of the item to document.  For example if
                this is a function then this will be the name of the function,
                no return types, no arguments.

            isattr (bool): Is the member an attribute.  This is unused for c
                documenation.

            parent (object): The parent item of this `member`.

        Returns:
            bool: True if this class can document the `member`.
        """
        return (
            isinstance(parent, CObjectDocumenter) and member.type == cls.directivetype
        )

    def parse_name(self) -> bool:
        """Determine what module to import and what attribute to document.

        .. note:: Sphinx autodoc supports args and return anotation, since
            this is targeting C and it isn't currently needed, these won't be
            supported by this implementation.

        Returns:
            bool: True if successfully parsed and sets :attr:`modname`,
                :attr:`objpath`, :attr:`fullname`.

                False if the signature couldn't be parsed.
        """
        c_autodoc_re = re.compile(r"^([\w\/\\.]+)(::([\w.]+\.)?(\w+))?\s*$")

        try:
            match = c_autodoc_re.match(self.name)
            fullname, _, path, base = match.groups()  # type: ignore
        except AttributeError:
            logger.warning(
                "invalid signature for auto%s (%r)" % (self.objtype, self.name),
                type="c_autodoc",
            )
            return False

        parents: List[str]
        if path is None:
            parents = []
        else:
            parents = path.rstrip(".").split(".")

        self.modname, self.objpath = self.resolve_name(fullname, parents, path, base)

        self.fullname = self.modname
        return True

    def resolve_name(
        self, modname: str, parents: List[str], path: Optional[str], base: str
    ) -> Tuple[str, List[str]]:
        """
        Resolve the module and object name of the object to document.
        This can be derived in two ways:

        - Naked: Where the argument is only the file/module name `my_file.c`
        - Double colons: Where the argument to the directive is of the form
          `my_file.c::some_func`.

        Args:
            modname (str): The filename of the c file (module)
            parents (list): The list split('.') version of path.

                - The filename without the extension when naked argument is used.
                - Any parents when double colon argument is used. For example
                  structs or unions of `my_struct.field_name` would have a
                  parents entry of ['my_struct']

            path (str): Two possible states:

                - None if `parents` is the empty list.
                - The ``'.'.join()`` version of `parents`, with a trailing ``.``.

            base (str): The name of the object to document. This will be None
                when the object to document is the c module

        Returns:
            tuple: (str, [str]) The module name, and the object names (if any).
        """
        if base:
            return modname, parents + [base]

        return modname, []

    def import_object(self) -> bool:
        """Load the C file and build up the document structure.

        This will load the C file's documented structure into :attr:`object`
        """
        for source_dir in self.env.config.c_autodoc_roots:
            filename = os.path.join(source_dir, self.get_real_modname())

            # Prefixing with "/" will force "absolute" path which is relative
            # to the source directory.
            rel_filename, filename = self.env.relfn2path(f"/{filename}")
            if os.path.isfile(filename):
                break
        else:
            logger.warning(
                "Unable to find file, %s, in any of the directories %s "
                "all directories are relative to the top documentation source directory"
                % (self.get_real_modname(), self.env.config.c_autodoc_roots),
                location=(self.env.docname, self.directive.lineno),
            )
            return False

        self.env.note_dependency(rel_filename)

        source_dict = getattr(self.env, "_viewcode_c_modules", {})
        self.env._viewcode_c_modules = source_dict  # type: ignore

        # TODO The :attr:`temp_data` is reset for each document ideally want to
        # use or make an attribute on `self.env` that is reset per run or just
        # not pickled.
        modules_dict = self.env.temp_data.setdefault("c:loaded_modules", {})

        if filename not in modules_dict:
            with open(filename) as f:
                contents = [f.read()]

            # let extensions preprocess files
            self.env.app.emit("c-autodoc-pre-process", filename, contents)
            modules_dict[filename] = loader.load(filename, contents[0])
            ast = json.loads(str(modules_dict[filename]))
            source_dict.setdefault(
                self.get_real_modname(), ViewCodeListing(contents[0], ast)
            )

        self.module = modules_dict[filename]

        self.object = self.module
        self.object_name = self.name

        # objpath is set when double colons are used in :meth:`resolve_name`.
        # i.e. this is a node or sub-node in a module.
        if self.objpath:
            for obj in self.objpath:
                self.object_name = obj
                self.object = self.object.children[self.object_name]  # type: ignore

        return True

    def get_doc(
        self, encoding: Optional[str] = None, ignore: int = 1
    ) -> List[List[str]]:
        """Decode and return lines of the docstring(s) for the object."""
        docstring = self.object.get_doc()
        tab_width = self.directive.state.document.settings.tab_width
        return [prepare_docstring(docstring, ignore, tab_width)]

    def get_object_members(self, want_all: bool) -> Tuple[bool, List[Tuple[str, Any]]]:
        """Return `(members_check_module, members)` where `members` is a
        list of `(membername, member)` pairs of the members of *self.object*.

        If *want_all* is True, return all members.  Else, only return those
        members given by *self.options.members* (which may also be none).
        """
        if want_all:
            return False, list(self.object.children.items())

        # The caller sets `want_all` if :attr:`options.members` is ALL, so it
        # should be safe to assume this is a list or None at this point.
        desired_members = self.options.members or []

        object_members: List[Tuple[str, Any]] = []
        for member in desired_members:
            if member in self.object.children:
                object_members.append((member, self.object.children[member]))
            else:
                logger.warning(
                    'Missing member "%s" in object "%s"' % (member, self.fullname),
                    type="c_autodoc",
                )

        return False, object_members

    def filter_members(
        self, members: List[Tuple[str, Any]], want_all: bool
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

    def format_args(self, **kwargs: Any) -> str:
        """
        Creates the parenthesis version of the function signature.  i.e. this
        will be the `(int hello, int what)` portion of the header.
        """
        return self.object.format_args(**kwargs)


class CModuleDocumenter(CObjectDocumenter):
    """
    This auto documenter will be registered as a directive named `autocmodule`,
    there may be a way to override the python `automodule`, just not sure yet...
    """

    objtype = "cmodule"
    directivetype = "module"

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        """
        Modules are top levels so should never be included as a child of another
        c object.

        Parameters:
            member (object): The member item to document.  This type is specific
                to the item being processed by autodoc.  These instances will
                only attempt to process
                :class:`sphinx_c_autodoc.loader.CObjectDocumenter`.

            membername (str): The name of the item to document.  For example if
                this is a function then this will be the name of the function,
                no return types, no arguments.

            isattr (bool): Is the member an attribute.  This is unused for c
                documenation.

            parent (object): The parent item of this `member`.

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

    objtype = "ctype"
    directivetype = "type"

    def __init__(
        self, directive: DocumenterBridge, name: str, indent: str = ""
    ) -> None:
        """
        Override the :attr:`directive` so that some post processing can be
        performed in :meth:`generate`
        """
        super().__init__(directive, name, indent)

        self._original_directive = self.directive
        self.directive = DocumenterBridge(
            self.directive.env,
            self.directive.reporter,
            self.directive.genopt,
            self.directive.lineno,
            self.directive.state,
        )

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        """
        The general type documenter can handle; structs, typedefs, unions and
        enums (Not the enumerations).

        Parameters:
            member (object): The member item to document.  This type is specific
                to the item being processed by autodoc.  These classes will
                only attempt to process
                :class:`sphinx_c_autodoc.loader.CObjectDocumenter` members.

            membername (str): The name of the item to document.  For example if
                this is a function then this will be the name of the function,
                no return types, no arguments.

            isattr (bool): Is the member an attribute.  This is unused for c
                documenation.

            parent (object): The parent item of this `member`.

        Returns:
            bool: True if this class can document the `member`.
        """
        return isinstance(parent, CObjectDocumenter) and member.type in (
            "enum",
            "struct",
            "type",
            "union",
        )

    def generate(
        self,
        more_content: Optional[StringList] = None,
        real_modname: Optional[str] = None,
        check_module: bool = False,
        all_members: bool = False,
    ) -> None:
        """
        generate stuff
        """
        super().generate(
            more_content=more_content,
            real_modname=real_modname,
            check_module=check_module,
            all_members=all_members,
        )

        self._original_directive.result.append(self.consolidate_members())

    def _find_member_directives(self, name: str) -> List[Tuple[str, str, int]]:
        """
        Find all directive lines which start with `` ..c:<name>::``.

        Creates a sequence of:

            - The short name of the item documented by the directive.
            - The full signature of the item documented.
            - The line number in :attr:`directive.results`.

        For intsnace a directive of ``..c:some_directive word1 word2 word3``
        would result in ``word3`` being the short name and
        ``word1 word2 word3`` being the full signature.

        Args:
            name (str): The name of the directive(s) to search for.

        Returns:
            list(tuple(str, str, int)): The short name, the full signature,
                and the line in :attr:`directive.results` where the
                directive occured.
        """
        members = []
        directive_string = f".. c:{name}::"
        for line_no, line in enumerate(self.directive.result):
            if not line.startswith(self.indent):
                continue

            if line.lstrip().startswith(directive_string):
                _, signature = line.split(directive_string)
                sig_parts = signature.strip().split()
                members.append((sig_parts[-1], signature, line_no))

        return members

    def _remove_directive(self, line: int) -> StringList:
        """
        Remove the directive which starts at `line_no` from
        :attr:`directive.results`. The locations in :attr:`directive.results`
        will be replaced with empty lines so that the total line count of
        :attr:`directive.results` is unaffected.

        Args:
            line (int): The starting line to remove the directive from.

        Returns:
            :class:`StringList`: The removed directive which started at `line_no`
        """

        # Just need to do at least one more indentation than the actual
        # directive to not end up grabbing the next directive.
        directive_line = self.directive.result[line]
        block_indent = (len(directive_line) - len(directive_line.lstrip())) + 1
        directive, _, _ = self.directive.result.get_indented(
            line, first_indent=0, block_indent=block_indent, strip_indent=False
        )
        directive.disconnect()

        # Setting slices need viewlists/stringlists so just iterate through and
        # set indices which can take strings
        directive_length = len(directive)
        for line_no in range(line, line + directive_length):
            self.directive.result[line_no] = self.indent

        return directive

    @staticmethod
    def _merge_directives(directives: List[StringList]) -> StringList:
        """
        Args:
            directives (list(StringList)): The list of directives to merge.

        Returns:
            StringList: One directive
        """
        merged_heading = StringList()
        merged_directive = StringList()
        merged_options = StringList()
        for directive in directives:
            options, _, _ = directive.get_indented(
                1, until_blank=True, strip_indent=False
            )
            if options:
                merged_options.extend(options)
                del directive[1 : 1 + len(options)]

            directive_heading = directive[0]
            del directive[0]

            merged_directive.extend(directive)
            if len(directive_heading) > len(merged_heading):
                merged_heading = directive_heading

        merged_directive.insert(0, merged_options)
        merged_directive.insert(0, merged_heading, source=merged_directive.source(0))
        return merged_directive

    def consolidate_members(self) -> StringList:
        """
        Take any duplicate autodoc member directives and consolidate them into
        one directive. The subsequent contents of duplicate directives will be
        added as additional paragraphs on the first occurrence of the directive.

        Returns:
            StringList: The entire rst contents for this directive instance.

        """
        # member is the normal native fields of a struct or union
        members = self._find_member_directives("member")
        # type is a struct or union declared in place in a struct or union
        members += self._find_member_directives("type")
        # macro is the enumeration constants for an enum type
        members += self._find_member_directives("macro")
        members.sort()
        data_blocks = []

        for _, member_group in groupby(members, lambda m: m[0]):
            start_line = len(self.directive.result)
            directives = []
            for _, _, line in member_group:
                directives.append(self._remove_directive(line))
                if line < start_line:
                    start_line = line
                    original_length = len(directives[-1])

            merged_directive = self._merge_directives(directives)
            data_blocks.append((start_line, original_length, merged_directive))

        data_blocks.sort()
        delta_length = 0
        for line, original_length, directive in data_blocks:
            start = line + delta_length
            end = start + original_length
            self.directive.result[start:end] = directive
            delta_length += len(directive) - original_length

        return self.directive.result


class CMemberDocumenter(CObjectDocumenter):
    """
    The documenter for the autocmember directive.

    This handles structure and union fields.
    """

    objtype = "cmember"
    directivetype = "member"


class CFunctionDocumenter(CObjectDocumenter):
    """
    The documenter for the autocfunction directive.
    """

    objtype = "cfunction"
    directivetype = "function"


class CMacroDocumenter(CObjectDocumenter):
    """
    The documenter for the autocmacro directive.
    """

    objtype = "cmacro"
    directivetype = "macro"


class CDataDocumenter(CObjectDocumenter):
    """
    The documenter for the autocdata directive.
    """

    objtype = "cdata"
    directivetype = "var"

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        """
        Parameters:
            member (object): The member item to document.  This type is specific
                to the item being processed by autodoc.  These classes will
                only attempt to process
                :class:`sphinx_c_autodoc.loader.CObjectDocumenter` members.

            membername (str): The name of the item to document.  For example if
                this is a function then this will be the name of the function,
                no return types, no arguments.

            isattr (bool): Is the member an attribute.  This is unused for c
                documenation.

            parent (object): The parent item of this `member`.

        Returns:
            bool: True if this class can document the `member`.
        """
        # Handle the mapping of c land `variable` to sphinx land `data`.  The c
        # domain in sphinx seems inconsistent the directive is called
        # ``.. c:var::``, yet the role is ``:c:data:``.
        return isinstance(parent, CObjectDocumenter) and member.type == "variable"


class CModule(CObject):
    """
    Module directive for C files
    """

    has_content = True
    required_arguments = 1

    def run(self) -> nodes.Node:
        """
        Not sure yet
        """
        state = self.state
        node = nodes.section()

        rst = ViewList(self.content, "testing")

        # Parse the restructured text into nodes.
        state.nested_parse(rst, 0, node, match_titles=1)

        return node.children


def setup(app: Sphinx) -> None:
    """
    Setup function for registering this with sphinx
    """
    app.require_sphinx("2.0")
    app.setup_extension("sphinx.ext.autodoc")
    app.add_autodocumenter(CModuleDocumenter)
    app.add_autodocumenter(CFunctionDocumenter)
    app.add_autodocumenter(CTypeDocumenter)
    app.add_autodocumenter(CMemberDocumenter)
    app.add_autodocumenter(CMacroDocumenter)
    app.add_autodocumenter(CDataDocumenter)
    app.add_directive_to_domain("c", "module", CModule)
    app.add_config_value("c_autodoc_roots", [""], "env")
    app.add_event("c-autodoc-pre-process")

    patch_c_domain()

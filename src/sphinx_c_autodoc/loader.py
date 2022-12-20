"""
Load the c file objects
"""

import json
import os
import re
import textwrap

from collections import OrderedDict, namedtuple
from itertools import takewhile
from typing import Any, List, Optional, Union, Dict, Tuple, Sequence

from bs4 import BeautifulSoup
from bs4.element import Tag
from clang import cindex
from clang.cindex import Cursor, Token, StorageClass

from sphinx_c_autodoc.clang.patches import patch_clang

#: Nodes which clang doesn't autopopulate with the associated comment
UNDOCUMENTED_NODES = (cindex.CursorKind.MACRO_DEFINITION,)

#: The first few characters of a comment which indicates a documentation comment.
DOCUMENTATION_COMMENT_START = ("/**", "/*!", "///")

#: The start of a comment that is meant to document the previous item
TRAILING_COMMENT_START = ("/**<", "/*!<", "///<")

#: Nodes which can be anonymous and still need to be documented. i.e.
#: anonymous structures are usually part of another node. Anonymous enums are
#: often used to use the enumerators but not force the type usage.
ALLOWED_ANONYMOUS = (cindex.CursorKind.ENUM_DECL,)

# Must do this prior to calling into clang
patch_clang()

#: A light container to mimic a :class:`cindex.Token` for comments.
PsuedoToken = namedtuple("PsuedoToken", ["spelling", "extent"])


class DocumentedObject:
    """
    A representation of a c object for documentation purposes.

    Arguments:
        node (:class:`~clang.cindex.Cursor`): The node representing this object.

    Attributes:
        type_ (str): The type of this item one of:

            - object: unknown/unsupported object.
            - file: Should be the root object of a documentation tree.
            - member: Member or field of a struct or union
            - function: A function
            - type: A typedef
            - struct: A structure
            - union: A Union
            - enumerator: An enumerator constant
            - macro: A macro

        doc (str): The default documentation of the object. This is usally
            the comment with leading '*' removed.
        name (str): The name of the object. For example functions this would
            be *only* the name of the function.
        node (:class:`~clang.cindex.Cursor`): The node representing this object.
        _children: The children of the object. For
            example for structs this would be the members or fields.
        _soup (:class:`~bs4.BeautifulSoup`): The soupified version of
            :attr:`node`'s clang xml comment.
        _declaration (str): The declaration string. For most things this is
            the type as well as the name.
        _line_range (Tuple[int, int]): The line range of the C construct,
            this will include any leading or trailing comments that may be
            part of the construct's documentation.
    """

    type_ = "object"

    def __init__(self, node: Cursor) -> None:
        self.doc = ""
        self.name = ""
        self.node = node
        self._children: Optional[OrderedDict] = None
        self._soup: Optional[BeautifulSoup] = None
        self._declaration: Optional[str] = None
        self._line_range: Optional[Tuple[int, int]] = None

    def line_range(self) -> Tuple[int, int]:
        """
        The lines in the source file that this object covers.

        This will include any leading or trailing comments that may be part
        of the construct's documentation.
        """
        if self._line_range is None:
            node_extent = self.node.extent
            comment_extent = self.node.comment_extent
            if comment_extent.start.file is None:
                comment_extent = node_extent

            self._line_range = (
                min(node_extent.start.line, comment_extent.start.line),
                max(node_extent.end.line, comment_extent.end.line),
            )

        return self._line_range

    @property
    def type(self) -> str:
        """
        The type of object
        """
        return self.type_

    @property
    def children(self) -> dict:
        """
        The child objects of this object.
        """
        if self._children is None:
            self._children = OrderedDict()

        return self._children

    # pylint: disable=no-self-use, unused-argument
    def format_args(self, **kwargs: Any) -> str:
        """
        Creates the parenthesis version of the function signature.  i.e. this
        will be the `(int hello, int what)` portion of a function.
        """
        return ""

    def format_name(self) -> str:
        """
        The name of the object.

        For things like functions and others this will include the return type.
        """
        return self.declaration

    def __str__(self) -> str:
        """
        Will turn this instance into a JSON like representation.
        """
        obj_dict: Dict[str, Any] = {}
        obj_dict["doc"] = self.doc
        obj_dict["type"] = self.type
        obj_dict["name"] = self.name

        line_range = self.line_range()
        obj_dict["start_line"] = line_range[0]
        obj_dict["end_line"] = line_range[1]

        obj_dict["children"] = []

        for child in self.children.values():
            obj_dict["children"].append(json.loads(str(child)))

        return json.dumps(obj_dict)

    def get_doc(self) -> str:
        """
        Get the documentation paragraph of the item
        """
        if self.soup is not None:
            root = self.soup.contents[0]
            body = self.get_paragraph(root.find("abstract", recursive=False))
            body += self.get_paragraph(root.find("discussion", recursive=False))
            return body

        return self.doc

    @property
    def declaration(self) -> str:
        """
        Declaration for this object. For things like functions it will be
        `void foo(int a, int b)` for variables it will be the type and name
        `char my_var`.
        """
        if self._declaration is None:
            # First try to utilize the clang comment's version as it is assumed
            # to be the more correct.
            self._declaration = self.get_soup_declaration()

        if self._declaration is None:
            # soup failed so fall back to manual parsing
            self._declaration = self.get_parsed_declaration()

        return self._declaration

    def get_parsed_declaration(self) -> str:
        """
        Get the declaration as parsed from the :attr:`node`. This may be
        specific to each :attr:`type`.
        """
        # Declarations are object specific so default to something sane in the
        # off chance an object fails to implement this.
        return self.name

    def get_soup_declaration(self) -> Optional[str]:
        """
        Get the declaration element from :attr:`soup`. If there is no soup or
        no declaration this will return None.
        """
        if self.soup is None:
            return None

        root = self.soup.contents[0]

        # It seems with different versions of clang the newlines will at times
        # be kept around from some declarations. This causes problems with
        # sphinx as the signature should remain all in one line.
        lines = root.declaration.text.splitlines()
        declaration = " ".join(line.strip() for line in lines)
        return declaration

    @property
    def soup(self) -> Optional[BeautifulSoup]:
        """
        Get the beautifulsoup representation of this object's comment.

        Returns:
            BeautifulSoup: The xml comment for this C object turned into soup.
        """
        if self._soup is None:
            comment = self.node.getParsedComment().as_xml()
            if comment is not None:
                self._soup = BeautifulSoup(comment, features="html.parser")

        return self._soup

    @staticmethod
    def get_paragraph(tag: Optional[Tag]) -> str:
        """
        Get the paragraph contents from `tag`.

        Args:
            tag (:class:`~BeautifulSoup.tag`): The tag to get the paragraph
                contents from.

        Returns:
            str: One of two things:
                - An empty string if `tag` is None.
                - All of the paragraph contents of `tag` with newlines
                  between them along with a trailing newline, otherwise.
        """
        if tag is None:
            return ""

        paragraph = "\n".join(p.text.strip() for p in tag.find_all("para"))
        paragraph += "\n"
        return paragraph

    def is_public(self) -> bool:
        """
        Determines if this item is public.

        C doesn't actually have public/private namespace so we're going to
        make up some rules.

        Constructs are public if:

            - They are in a header file. By nature header files are meant to
              be included in other files, thus they are deamed public.

            - They can be visible outside of the compilation unit. These are
              things the linker can get access to. Mainly this means functions
              and variables that are not static.
        """
        # Here we'll do the most common logic, and let specific constructs that
        # can be public do special logic.
        if self.node.location.file.name.endswith(".h"):
            return True

        return False


class DocumentedFile(DocumentedObject):
    """
    A documented file
    """

    type_ = "file"


class DocumentedMacro(DocumentedObject):
    """
    A documented macro
    """

    type_ = "macro"

    def format_args(self, **kwargs: Any) -> str:
        """
        If the macro is function like, gets the parenthesis version of the
        function signature. i.e. this will be the `(_x, _y)` portion of the
        macro function header.
        Otherwise this is the empty string.

        Returns:
            The argument string for this macro.
        """
        decl = self.declaration

        # The logic allows this to be used for both function like and non
        # function like macros.
        # 'SOME_DEFINE'.partition('(')
        # >>>  'SOME_DEFINE', '', ''
        #
        # 'FUNCTION_LIKE(_a, _b)'.partition('(')
        # >>>  'FUNCTION_LIKE', '(', '_a, _b)'
        _, part, args = decl.partition("(")
        return part + args

    def format_name(self) -> str:
        """Format the name for use in sphinx.

        For things like functions and others this will include the return type.
        """
        decl = self.declaration
        name, _, _ = decl.partition("(")
        return name

    def get_parsed_declaration(self) -> str:
        """
        Creates the full declaration of the macro. For function like macros
        this will include the parenthesised arguments.
        """
        if not self.node.is_macro_function_like():
            return f"{self.name}"

        # We know this must be a function like macro, which means the first 2
        # tokens are `MACRO_NAME` followed by `(`.
        token_iter = self.node.get_tokens()
        next(token_iter)
        next(token_iter)

        # Consume all identifier tokens until the first closing `)`. This will
        # skip over `,` as well as any inline comments.
        # This may have some false positives if there are extra parens in the
        # argument list
        ident_iter = takewhile(lambda x: x.spelling != ")", token_iter)
        tokens = [
            i.spelling for i in ident_iter if i.kind == cindex.TokenKind.IDENTIFIER
        ]

        return f"{self.name}({', '.join(tokens)})"


class DocumentedEnumerator(DocumentedMacro):
    """
    An enumerator, the constant values in an enum
    """

    type_ = "enumerator"


class DocumentedMember(DocumentedObject):
    """
    A documented member of a struct or union.
    """

    type_ = "member"

    def get_parsed_declaration(self) -> str:
        """
        Build up the name from the node. This should be the member's type and
        it's name. i.e. for::

            struct foo
            {
                int bar;
                float hello;
            };

        The parsed declaration of `bar` would be `int bar`.
        """
        type_ = self.node.type.spelling

        # Libclang will return the type as `float [20]` when looking at
        # `float foo[20]`.  We could look at the kind `TypeKind.CONSTANTARRAY`
        # but partitioning on the "[" just seems more straight forward.
        type_, *(array) = type_.partition("[")
        array_contents = "".join(array)
        return f"{type_} {self.name} {array_contents}"

    def is_public(self) -> bool:
        """
        Members are always public, because it's their parents that determine
        public versus private.
        """
        return True


class DocumentedFunction(DocumentedObject):
    """
    A function specific documented object.
    """

    type_ = "function"

    def get_soup_doc(self) -> Optional[str]:
        """
        Gets the documentation from the :attr:`_soup`.
        """
        if self.soup is None:
            return None
        root = self.soup.contents[0]

        if not root.find("parameters", recursive=False) and not root.find(
            "resultdiscussion"
        ):
            return None

        body = self.get_paragraph(root.find("abstract", recursive=False))
        body += self.get_paragraph(root.find("discussion", recursive=False))

        # Single newlines are tread as the same paragraph in restructured text,
        # providing 2 results in separate paragraphs.
        body = body.replace("\n", "\n\n")

        for param in root.find_all("parameter"):
            name = param.find("name").text
            param_doc = self.get_paragraph(param.discussion)
            body += f"\n:param {name}: {param_doc}"

        returns = self.get_paragraph(root.find("resultdiscussion", recursive=False))
        if returns:
            body += f"\n:returns: {returns}"

        return body

    def get_doc(self) -> str:
        """
        Get the documentation paragraph of the item
        """
        soup_doc = self.get_soup_doc()
        if soup_doc is not None:
            return soup_doc

        return self.doc

    def format_args(self, **kwargs: Any) -> str:
        """
        Creates the parenthesis version of the function signature.  i.e. this
        will be the `(int hello, int what)` portion of the function header.
        """
        decl = self.declaration
        _, args = decl.split("(", 1)
        return "(" + args

    def format_name(self) -> str:
        """Format the name of *self.object*.

        This normally should be something that can be parsed by the generated
        directive, but doesn't need to be (Sphinx will display it unparsed
        then).

        For things like functions and others this will include the return type.
        """
        decl = self.declaration
        name, _ = decl.split("(", 1)
        return name

    def _get_arguments(self) -> str:
        """
        Get the arguments for this instance.

        Returns:
            str: The arguments for use in the function signature.
        """
        func = self.node

        # Early logic used to iterate over, `func.get_arguments()`, however when there
        # is an unknown type clang will sometimes fail to provide tokens for that
        # argument. For example in "unknown_type foo[]" the brackets will cause clang
        # to return back no tokens for the argument.
        start = func.location
        end = func.extent.end
        if func.is_definition():
            # When a function is a definition the last child is the compound statement
            # so we need to move prior to the compound statement
            children = list(func.get_children())
            body_start = children[-1].extent.start.offset
            end = cindex.SourceLocation.from_offset(func.tu, start.file, body_start - 1)

        extent = cindex.SourceRange.from_locations(start, end)
        non_comment_tokens = (
            t
            for t in cindex.TokenGroup.get_tokens(func.tu, extent=extent)
            if t.kind != cindex.TokenKind.COMMENT
        )

        # Even though this will place spaces around all the tokens, the sphinx C domain
        # will provide some formatting to make it look nicer in the final output.
        full_signature = " ".join(t.spelling for t in non_comment_tokens)

        _, _, arguments = full_signature.partition("(")
        arguments = arguments.rstrip(")")
        arguments = arguments.strip()

        return arguments

    def get_parsed_declaration(self) -> str:
        """
        Creates the parenthesis version of the function signature.  i.e. this
        will be the `(int hello, int what)` portion of the header.
        """
        args = self._get_arguments()

        func = self.node
        tu = func.tu

        # For functions the extent encompasses the return value, and the
        # location is the beginning of the functions name.  So we can consume
        # all tokens in between.
        end = cindex.SourceLocation.from_offset(
            tu, func.location.file, func.location.offset - 1
        )
        extent = cindex.SourceRange.from_locations(func.extent.start, end)

        return_type = " ".join(
            t.spelling for t in cindex.TokenGroup.get_tokens(tu, extent=extent)
        )

        return f"{return_type} {func.spelling}({args})"

    def is_public(self) -> bool:
        """
        Functions are public as long as they are not static.
        """
        if self.node.storage_class == StorageClass.STATIC:
            return False

        return True


class DocumentedType(DocumentedObject):
    """
    A documented type(def)
    """

    type_ = "type"

    def get_parsed_declaration(self) -> str:
        """Format the name of *self.object*.

        This normally should be something that can be parsed by the generated
        directive, but doesn't need to be (Sphinx will display it unparsed
        then).

        For things like functions and others this will include the return type.
        """
        parent_type = self.node.underlying_typedef_type.spelling

        # Function prototypes need to be handled different. When clang can't
        # successfully parse the file it falls back to naming the return type
        # as the display name.
        # Unfortunately some versions of clang behave a little differently, some
        # will return a `POINTER` while others will return `FUNCITONNOPROTO`. The
        # `POINTER`s are easy to derive the real type from, but the test
        # environment doesn't use that version of clang.
        type_ = self.node.underlying_typedef_type
        if type_.kind == cindex.TypeKind.POINTER:  # pragma: no cover
            type_ = type_.get_pointee()

        if type_.kind in (
            cindex.TypeKind.FUNCTIONPROTO,
            cindex.TypeKind.FUNCTIONNOPROTO,
        ):
            ret_value, paren, signature = parent_type.partition(")")
            signature = "".join((ret_value, self.name, paren, signature))

            return f"typedef {signature}"

        return f"typedef {parent_type} {self.name}"


class DocumentedStructure(DocumentedObject):
    """
    A documented structure
    """

    type_ = "struct"

    @property
    def soup(self) -> None:
        """
        Since structures like objects use the "Members:" and
        "Enumerators:" sections do *not* use the clang xml comments as they
        don't preserve newlines, so the sections get lost.
        """
        return None

    def get_parsed_declaration(self) -> str:
        """
        Structures, and similar, are just name.
        """
        return f"{self.name}"

    @property
    def children(self) -> dict:
        """
        Gets the children, members, of the structure.
        """
        if self._children is None:
            # Get the first level of the structures members.
            struct = self.node
            self._children = OrderedDict()
            for member in struct.get_children():
                item = object_from_cursor(member)
                if item:
                    self._children[member.spelling] = item

        return self._children


class DocumentedUnion(DocumentedStructure):
    """
    Class for unions. Same as structures with a different :attr:`type`.
    """

    type_ = "union"


class DocumentedEnum(DocumentedStructure):
    """
    Class for Enums. Same as structures with a different :attr:`type`.
    """

    type_ = "enum"


class DocumentedVariable(DocumentedObject):
    """
    Class for file level variables
    """

    type_ = "variable"

    def format_name(self) -> str:
        """Format the name of *self.object*.

        This normally should be something that can be parsed by the generated
        directive, but doesn't need to be (Sphinx will display it unparsed
        then).

        For things like functions and others this will include the return type.
        """
        decl = self.declaration

        # variables which are declared and assigned at the same location will
        # include the assignment in the clange declaration, so strip it out for
        # documentation.
        name, _, _ = decl.partition("=")
        return name

    def is_public(self) -> bool:
        """
        Variables are public as long as they are not static.
        """
        if self.node.storage_class == StorageClass.STATIC:
            return False

        return True

    def get_parsed_declaration(self) -> str:
        """
        Get the declaration as parsed from the :attr:`node`.
        """
        # Libclang will return the type as `float [20]` when looking at
        # `float foo[20]`.  We could look at the kind `TypeKind.CONSTANTARRAY`
        # but partitioning on the "[" just seems more straight forward.
        type_ = self.node.type.spelling
        type_, *(array) = type_.partition("[")
        array_contents = "".join(array)

        real_type = self._find_declaration_type()
        type_ = type_.replace("int", real_type)

        return f"{type_} {self.name} {array_contents}"

    def _find_declaration_type(self) -> str:
        """
        Makes an attempt to try and find the identifier, and storage class,
        representing the variable type.

        Returns:
            str: The type of the variable.  If this can't be derived falls back to
                `int`.
        """
        type_ = "int"
        tokens = list(
            filter(
                lambda t: t.kind == cindex.TokenKind.IDENTIFIER, self.node.get_tokens()
            )
        )
        try:
            type_ = tokens[-2].spelling
        except IndexError:
            # For array variables with unknown types libclang fails to provide the
            # tokens.
            pass

        # clang doesn't provide the storage class in the type name, so we'll add it here
        storage_keyword = ""
        storage_class = self.node.storage_class
        if storage_class == cindex.StorageClass.STATIC:
            storage_keyword = "static"
        if storage_class == cindex.StorageClass.EXTERN:
            storage_keyword = "extern"

        return f"{storage_keyword} {type_}"


CURSORKIND_TO_OBJECT_CLASS = {
    cindex.CursorKind.TRANSLATION_UNIT: DocumentedFile,
    cindex.CursorKind.FUNCTION_DECL: DocumentedFunction,
    cindex.CursorKind.STRUCT_DECL: DocumentedStructure,
    cindex.CursorKind.UNION_DECL: DocumentedUnion,
    cindex.CursorKind.ENUM_DECL: DocumentedEnum,
    cindex.CursorKind.FIELD_DECL: DocumentedMember,
    cindex.CursorKind.MACRO_DEFINITION: DocumentedMacro,
    cindex.CursorKind.ENUM_CONSTANT_DECL: DocumentedEnumerator,
    cindex.CursorKind.VAR_DECL: DocumentedVariable,
    cindex.CursorKind.TYPEDEF_DECL: DocumentedType,
}


def object_from_cursor(cursor: Cursor) -> Optional[DocumentedObject]:
    """
    Create an instance from a :class:`cindex.Cursor`
    """
    # Spelling is always good on the "primary" node.
    name = cursor.spelling

    if not name:
        # An anonymous construct which isn't contained in a typedef will have a
        # type spelling of:
        # "<construct> (anonymous at # <path_to_c_file>:<lineno>)"
        # Typedef's should be handled by the get_nested_node() function
        if cursor.kind in ALLOWED_ANONYMOUS and any(
            anon in cursor.type.spelling for anon in ("anonymous at", "unnamed at")
        ):
            filename = os.path.basename(cursor.location.file.name)
            # remove the extension from the filename since the '.' is not a
            # valid c identifier. splitext will remove the trailing most
            # extension so if this file is multi dotted it will fail, just use
            # partition and grab the first part.
            filename, _, _ = filename.partition(".")
            name = f"anon_{filename}_{cursor.hash}"
        else:
            # Don't document anonymous items
            return None

    nested_cursor = get_nested_node(cursor)
    class_ = CURSORKIND_TO_OBJECT_CLASS.get(nested_cursor.kind, DocumentedObject)
    doc = class_(nested_cursor)

    doc.name = name
    psuedo_comment = PsuedoToken(
        nested_cursor.raw_comment, nested_cursor.comment_extent
    )
    doc.doc = parse_comment(psuedo_comment)

    return doc


def get_nested_node(cursor: Cursor) -> Cursor:
    """
    Retrieve the nested node that `cursor` may be shadowing
    """
    if cursor.kind in (
        cindex.CursorKind.TYPEDEF_DECL,
        cindex.CursorKind.FIELD_DECL,
        cindex.CursorKind.VAR_DECL,
    ):
        try:
            underlying_node = next(cursor.get_children())
            if underlying_node.kind in (
                cindex.CursorKind.STRUCT_DECL,
                cindex.CursorKind.UNION_DECL,
                cindex.CursorKind.ENUM_DECL,
            ):
                return underlying_node
        except StopIteration:
            # No children for typedefs of native types, i.e. `typedef int some_int;`
            pass

    return cursor


def get_file_comment(cursor: Cursor, child: Optional[Cursor]) -> str:
    """
    Attempts to get the comment at the top of the file.

    Args:
        cursor (:class:`cindex.Cursor`): The root cursor of the file.
        child (:class:`cindex.Cursor`): The first child node in the file.
            This can be None.

    Returns:
        str: The file level comment.
    """
    try:
        token = next(cursor.get_tokens())
    except StopIteration:
        # Only happens with a completely empty file
        return ""

    if token.kind == cindex.TokenKind.COMMENT:
        if child is not None:
            child_comment = child.raw_comment
        else:
            child_comment = ""

        # if the first comment is not the documentation comment for the first
        # child then assume it is the file comment.
        if child_comment != token.spelling:
            return parse_comment(token)

    return ""


def get_compilation_args(
    filename: str, compilation_database: Optional[str] = None
) -> List[str]:
    """
    Get the compilation args for `filename` for the compilation database found in
    `compilation_db_dir`

    Args:
        filename (str): The file to get the compilation arguments for.
        compilation_database (str): The compilation database.

    Returns:
        list[str]: The compilation arguments.
    """
    if not compilation_database:
        return []
    directory = os.path.dirname(compilation_database)
    comp_db = cindex.CompilationDatabase.fromDirectory(directory)
    commands = comp_db.getCompileCommands(filename)

    if not commands:
        return []

    # For now only handling the first file instance seen in the database.
    # First argument is compiler path, last is the file to compile
    args = list(commands[0].arguments)[1:-1]

    # Since things like includes and defines could be relative we force the working
    # directory.
    working_dir = commands[0].directory
    args.append(f"-working-directory={working_dir}")

    return args


def load(
    filename: str,
    contents: str,
    compilation_database: Optional[str] = None,
    compilation_args: Optional[Sequence[str]] = None,
) -> DocumentedObject:
    """
    Load a C file into a tree of :class:`DocumentedObject`\'s

    Args:
        filename (str): The c file to load into a documented item
        contents (str): The contents of `filename`
        compilation_database (str): The compilation database.
        compilation_args (str): Compilation arguments.  Will be applied *after*
            compilation database.

    Returns:
        :class:`DocumentedObject`: The documented version of `filename`.

    """
    args = get_compilation_args(filename, compilation_database)
    if compilation_args:
        args += compilation_args

    tu = cindex.TranslationUnit.from_source(
        filename,
        args=args,
        unsaved_files=[
            (filename, contents),
        ],
        options=cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD,
    )
    cursor = tu.cursor

    root_document = DocumentedFile(cursor)

    # Some nodes show up from header includes as well as compiler defines, so
    # skip those. Macro instantiations are the locations where macros are
    # expanded, no need to document these.
    child_nodes = [
        c
        for c in cursor.get_children()
        if c.location.isFromMainFile()
        and c.kind
        not in (
            cindex.CursorKind.MACRO_INSTANTIATION,
            cindex.CursorKind.INCLUSION_DIRECTIVE,
        )
    ]

    # Macro definitions always come first in the child list, but that may not
    # be their location in the file, so sort all the nodes by location
    sorted_nodes = sorted(child_nodes, key=lambda x: x.extent.start.offset)

    comment_nodes(cursor, sorted_nodes)

    # TODO need to consider a better way to build this up, taking the
    # dictionary and modifying in place isn't ideal.
    children = root_document.children
    for node in sorted_nodes:
        item = object_from_cursor(node)
        if item:
            children[item.name] = item

    root_document.doc = cursor.raw_comment
    root_document.name = os.path.basename(cursor.spelling)
    root_document.node = cursor

    return root_document


def comment_nodes(cursor: Cursor, children: List[Cursor]) -> None:
    """
    Comment all nodes in `cursor` and `children` that fall into the
    :data:`UNDOCUMENTED_NODES` type of nodes.

    The nodes will be modified in place.

    Args:
        cursor (cindex.Cursor): The parent cursor of the child nodes
            which may need to be commented. This is assumed to be the root
            file cursor.

        children (Sequence(cindex.Cursor)): The child nodes which may need to
            be commented.
    """
    # The idea here is to look for comment tokens between nodes.
    tu = cursor.tu
    prev_child = None
    for child in children:
        # :func:`comment_node` will look to see if the node is in
        # UNDOCUMENTED_NODES, but do it here anyway to save the effort of
        # getting tokens, no performance metrics were checked, but the general
        # hunch is there will be a lot fewer UNDOCUMENTED_NODES than not.
        if child.kind not in UNDOCUMENTED_NODES:
            prev_child = child
            continue

        # This may not be 100% accurate but move the end to the previous
        # line. This solves problems like macro definitions not including the
        # preprocessor `#define` tokens.
        #
        #                             <-- previous line
        #     #define SOME_MACRO 23
        #             ^            ^ (Note `end` is exclusive)
        #             |            |
        #             +-- extent --+
        #
        location = child.extent.start
        end = cindex.SourceLocation.from_position(
            tu, location.file, location.line - 1, 1
        )

        start = prev_child.extent.end if prev_child else cursor.extent.start
        extent = cindex.SourceRange.from_locations(start, end)
        tokens = list(cindex.TokenGroup.get_tokens(tu, extent=extent))

        if tokens:
            comment_node(child, tokens[-1])
            comment_node(prev_child, tokens[0], trailing=True)

        prev_child = child

    first_child = children[0] if children else None
    cursor.raw_comment = get_file_comment(cursor, first_child)


def comment_node(node: Optional[Cursor], token: Token, trailing: bool = False) -> None:
    """
    Add the comment, `token`, to the `node`.

    node will be unmodified if:

        - `node` is not one of the :data:`UNDOCUMENTED_NODE`
        - `token` is not a documentation comment.

    Args:
        node (Cursor): The node to attempt to comment.
        token (Token): The token to use for the commenting.
        trailing (bool): Only comment `node` if `token` is a trailing
            comment, :data:`TRAILING_COMMENT_START`. If False then only
            comment `node` if `token` is a non trailing documentation
            comment.
    """
    if node is None or node.kind not in UNDOCUMENTED_NODES:
        return

    # DOCUMENTATION_COMMENT_START are all sub-strings of TRAILING_COMMENT_START
    # so either one would quickly be rejected here.
    if token.kind != cindex.TokenKind.COMMENT or not token.spelling.startswith(
        DOCUMENTATION_COMMENT_START
    ):
        return

    if trailing != token.spelling.startswith(TRAILING_COMMENT_START):
        return

    node.raw_comment = token.spelling
    node.comment_extent = token.extent


def parse_comment(comment: Union[Token, PsuedoToken]) -> str:
    """
    Clean up a C comment such that it no longer has leading `/**`, leading lines
    of `*` or trailing `*/`

    Args:
        comment (:class:`cindex.Token`): A c comment token from clang.

    Returns:
        str: The comment with the c comment syntax removed.
    """
    # Happens when there is no documentation comment in the source file for the
    # item.
    spelling = comment.spelling
    if spelling is None:
        return ""

    # Comments from clang start at the '/*' portion, but if the comment itself
    # is indented subsequent lines will have too much indent.
    # Transform::
    #
    #      "/**\n     * hello some comment\n     * on multiple lines\n     */"
    #
    # into::
    #
    #      "/**\n * hello some comment\n * on multiple lines\n */"
    indent = " " * (comment.extent.start.column - 1)
    indented_comment = indent + spelling
    dedented_comment = textwrap.dedent(indented_comment)

    # Notes on the regex here.
    #   Option 1 '\s?\*/?'
    #       This piece will match comment lines that start with '*' or ' *'.
    #       This will also match a trailing '*/' for the end of a comment
    #
    #   Option 2 '^/\*+<?'
    #       This will match the start of a comment '/*' and consume any
    #       subsequent '*'. This is also meant to catch '/**<' for trailing comments.
    #
    #   Option 3 '\*+/'
    #       Matches any and all '*' up to the end of the comment string.
    contents = re.sub(
        r"^\s?\*/?|^/\*+<?|\*+/",
        lambda x: len(x.group(0)) * " ",
        dedented_comment,
        flags=re.MULTILINE,
    )

    contents = textwrap.dedent(contents)

    # there may still be left over newlines so only strip those, but leave any
    # whitespaces.
    contents = contents.strip("\n")

    return contents

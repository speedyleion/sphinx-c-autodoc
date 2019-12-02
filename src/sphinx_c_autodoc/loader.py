"""
Load the c file objects
"""

import json
import os
import re
import textwrap

from collections import OrderedDict
from itertools import takewhile

from bs4 import BeautifulSoup
from clang import cindex

from sphinx_c_autodoc.clang.patches import patch_clang

UNDOCUMENTED_NODES = (cindex.CursorKind.MACRO_DEFINITION,)
DOCUMENTATION_COMMENT_START = ('/**', '/*!', '///')

# Must do this prior to calling into clang
patch_clang()


class DocumentedObject:
    """
    A representation of a c object for documentation purposes.

    Attributes:
        type (str): The type of this item one of:

            - object: unknown/unsupported object.
            - file: Should be the root object of a documentation tree.
            - member: Member or field of a struct or union
            - function: A function
            - type: A typedef
            - struct: A structure
            - union: A Union
        doc (str): The default documentation of the object. This is usally
            the comment with leading '*' removed.
        name (str): The name of the object. For example functions this would
            be *only* the name of the function.
        node (:class:`~clang.cindex.cursor`): The node representing this object.
        children (dict(DocumentedObject)): The children of the object. For
            example for structs this would be the members or fields.
        soup (:class:`~bs4.BeautifulSoup`): The soupified version of
            :attr:`node`'s clang xml comment.
        declaration (str): The declaration string. For most things this is
            the type as well as the name.

    """
    _type = 'object'

    def __init__(self):
        self.doc = ''
        self.name = ''
        self.node = None
        self._children = None
        self._soup = None
        self._declaration = None

    @property
    def type(self) -> str:
        """
        The type of object
        """
        return self._type

    @property
    def children(self) -> dict:
        """
        The child objects of this object.
        """
        if self._children is None:
            self._children = OrderedDict()

        return self._children

    # pylint: disable=no-self-use, unused-argument
    def format_args(self, **kwargs) -> str:
        """
        Creates the parenthesis version of the function signature.  i.e. this
        will be the `(int hello, int what)` portion of a function.
        """
        return ''

    def format_name(self) -> str:
        """
        The name of the object.

        For things like functions and others this will include the return type.
        """
        return self.declaration

    def __str__(self):
        """
        Will turn this instance into a JSON like representation.
        """
        obj_dict = {}
        obj_dict['doc'] = self.doc
        obj_dict['type'] = self.type
        obj_dict['name'] = self.name
        if self.children:
            obj_dict['children'] = []

            # TODO update this JSON representation to reflect the ordered dict
            for child in self.children.values():
                obj_dict['children'].append(json.loads(str(child)))

        return json.dumps(obj_dict)

    def get_doc(self) -> str:
        """
        Get the documentation paragraph of the item
        """
        if self.soup is not None:
            root = self.soup.contents[0]
            body = self.get_paragraph(root.find('abstract', recursive=False))
            body += self.get_paragraph(root.find('discussion', recursive=False))
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

    def get_soup_declaration(self) -> str:
        """
        Get the declaration element from :attr:`soup`. If there is no soup or
        no declaration this will return None.
        """
        if self.soup is None:
            return None

        root = self.soup.contents[0]

        return root.declaration.text

    @property
    def soup(self):
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
    def get_paragraph(tag) -> str:
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
            return ''

        paragraph = '\n'.join(p.text.strip() for p in tag.find_all('para'))
        paragraph += '\n'
        return paragraph


class DocumentedFile(DocumentedObject):
    """
    A documented file
    """
    _type = 'file'


class DocumentedMacro(DocumentedObject):
    """
    A documented macro
    """
    # Macros can be function like or they can be macro like so look up in the
    # :attr:`type`.
    _type = None

    @property
    def type(self) -> str:
        """
        Type of this object
        :return: The type
        """
        if self._type is None:
            if self.node.is_macro_function_like():
                self._type = 'function'
            else:
                self._type = 'macro'

        return self._type

    def format_args(self, **kwargs) -> str:
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
        _, part, args = decl.partition('(')
        return part + args

    def format_name(self) -> str:
        """Format the name for use in sphinx.

        For things like functions and others this will include the return type.
        """
        decl = self.declaration
        name, _, _ = decl.partition('(')
        return name

    def get_parsed_declaration(self) -> str:
        """
        Creates the full declaration of the macro. For function like macros
        this will include the parenthesised arguments.
        """
        if self.type == 'macro':
            return f'{self.name}'

        # We know this must be a function like macro, which means the first 2
        # tokens are `MACRO_NAME` followed by `(`.
        token_iter = self.node.get_tokens()
        next(token_iter)
        next(token_iter)

        # Consume all identifier tokens until the first closing `)`. This will
        # skip over `,` as well as any inline comments.
        # This may have some false positives if there are extra parens in the
        # argument list
        ident_iter = takewhile(lambda x: x.spelling != ')', token_iter)
        tokens = [i.spelling for i in ident_iter
                  if i.kind == cindex.TokenKind.IDENTIFIER]

        return '{}({})'.format(self.name, ', '.join(tokens))


class DocumentedMember(DocumentedObject):
    """
    A documented member of a struct or union.
    """
    _type = 'member'

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
        return f'{type_} {self.name}'


class DocumentedFunction(DocumentedObject):
    """
    A function specific documented object.
    """
    _type = 'function'

    def get_soup_doc(self) -> str:
        """
        Gets the documentation from the :attr:`_soup`.
        """
        root = self.soup.contents[0]
        body = self.get_paragraph(root.find('abstract', recursive=False))
        body += self.get_paragraph(root.find('discussion', recursive=False))

        for param in root.find_all('parameter'):
            name = param.find('name').text
            param_doc = self.get_paragraph(param.discussion)
            body += f'\n:param {name}: {param_doc}'

        returns = self.get_paragraph(root.find('resultdiscussion', recursive=False))
        if returns:
            body += f'\n:returns: {returns}'

        return body

    def get_doc(self) -> str:
        """
        Get the documentation paragraph of the item
        """
        if self.soup is not None:
            root = self.soup.contents[0]
            if root.find('parameters', recursive=False) or \
                    root.find('resultdiscussion'):
                return self.get_soup_doc()

        return self.doc

    def format_args(self, **kwargs) -> str:
        """
        Creates the parenthesis version of the function signature.  i.e. this
        will be the `(int hello, int what)` portion of the function header.
        """
        decl = self.declaration
        _, args = decl.split('(', 1)
        return '(' + args

    def format_name(self) -> str:
        """Format the name of *self.object*.

        This normally should be something that can be parsed by the generated
        directive, but doesn't need to be (Sphinx will display it unparsed
        then).

        For things like functions and others this will include the return type.
        """
        decl = self.declaration
        name, _ = decl.split('(', 1)
        return name

    def get_parsed_declaration(self) -> str:
        """
        Creates the parenthesis version of the function signature.  i.e. this
        will be the `(int hello, int what)` portion of the header.
        """
        func = self.node
        args = []
        for arg in func.get_arguments():
            args.append(' '.join(t.spelling for t in arg.get_tokens()))

        tu = func.tu

        # For functions the extent encompasses the return value, and the
        # location is the beginning of the functions name.  So we can consume
        # all tokens in between.
        end = cindex.SourceLocation.from_offset(tu, func.location.file,
                                                func.location.offset - 1)
        extent = cindex.SourceRange.from_locations(func.extent.start, end)

        return_type = ' '.join(t.spelling for t in
                               cindex.TokenGroup.get_tokens(tu, extent=extent))

        return '{} {}({})'.format(return_type, func.spelling, ', '.join(args))


class DocumentedType(DocumentedObject):
    """
    A documented type(def)
    """
    _type = 'type'

    def get_parsed_declaration(self) -> str:
        """Format the name of *self.object*.

        This normally should be something that can be parsed by the generated
        directive, but doesn't need to be (Sphinx will display it unparsed
        then).

        For things like functions and others this will include the return type.
        """
        parent_type = self.node.underlying_typedef_type.spelling
        return f'typedef {parent_type} {self.name}'


class DocumentedStructure(DocumentedObject):
    """
    A documented structure
    """
    _type = 'struct'

    @property
    def soup(self):
        """
        Since structures like objects use the "Members:" and
        "Enumerations:" sections do *not* use the clang xml comments as they
        don't preseve newlines, so the sections get lost.
        """
        return None

    def get_parsed_declaration(self) -> str:
        """
        Structures, and similar, are just the type and the name.
        """
        return f'{self.type} {self.name}'

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
    _type = 'union'


class DocumentedEnum(DocumentedStructure):
    """
    Class for unions. Same as structures with a different :attr:`type`.
    """
    _type = 'enum'


CURSORKIND_TO_OBJECT_CLASS = {cindex.CursorKind.TRANSLATION_UNIT: DocumentedFile,
                              cindex.CursorKind.FUNCTION_DECL: DocumentedFunction,
                              cindex.CursorKind.STRUCT_DECL: DocumentedStructure,
                              cindex.CursorKind.UNION_DECL: DocumentedUnion,
                              cindex.CursorKind.ENUM_DECL: DocumentedEnum,
                              cindex.CursorKind.FIELD_DECL: DocumentedMember,
                              cindex.CursorKind.MACRO_DEFINITION: DocumentedMacro,
                              cindex.CursorKind.ENUM_CONSTANT_DECL: DocumentedMacro,
                              cindex.CursorKind.TYPEDEF_DECL: DocumentedType}


def object_from_cursor(cursor):
    """
    Create an instance from a :class:`cindex.Cursor`
    """
    # Spelling is always good on the "primary" node.
    name = cursor.spelling

    # Don't document anonymous items
    if not name:
        return None

    nested_cursor = get_nested_node(cursor)
    class_ = CURSORKIND_TO_OBJECT_CLASS.get(nested_cursor.kind, DocumentedObject)
    doc = class_()

    doc.name = name
    doc.doc = parse_comment(nested_cursor.raw_comment)
    doc.node = nested_cursor

    return doc


def get_nested_node(cursor):
    """
    Retrieve the nested node that `cursor` may be shadowing
    """
    if cursor.kind in (cindex.CursorKind.TYPEDEF_DECL, cindex.CursorKind.FIELD_DECL):
        try:
            underlying_node = next(cursor.get_children())
            if underlying_node.kind in (cindex.CursorKind.STRUCT_DECL,
                                        cindex.CursorKind.ENUM_DECL):
                return underlying_node
        except StopIteration:
            # No children for typedefs of native types, i.e. `typedef int some_int;`
            pass

    return cursor


def get_root_comment(cursor, child):
    """
    Attempts to get the comment at the top of the file.
    """
    try:
        token = next(cursor.get_tokens())
    except StopIteration:
        # Only happens with a completely empty file
        return ''

    if token.kind == cindex.TokenKind.COMMENT:
        if child is not None:
            child_comment = child.raw_comment
        else:
            child_comment = ''

        # When the first comment is for the first node then the file lacks a
        # dedicated comment.
        if child_comment != token.spelling:
            return parse_comment(token.spelling)

    return ''


def load(filename):
    """
    Load a C file into a tree of :class:`DocumentedObject`\'s

    Args:
        filename (str): The c file to load into a documented item

    Returns:
        :class:`DocumentedObject`: The documented version of `filename`.

    """

    tu = cindex.TranslationUnit.from_source(filename,
                                            options=cindex.TranslationUnit.
                                            PARSE_DETAILED_PROCESSING_RECORD)
    cursor = tu.cursor

    root_document = DocumentedFile()

    # Some nodes show up from header includes as well as compiler defines, so
    # skip those. Macro instantiations are the locations where macros are
    # expanded, no need to document these.
    child_nodes = [c for c in cursor.get_children() if c.location.isFromMainFile()
                   and c.kind != cindex.CursorKind.MACRO_INSTANTIATION]

    # Macro definitions always come first in the child list, but that may not
    # be their location in the file, so sort all of the nodes by location
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


def comment_nodes(cursor, children):
    """
    Comment all nodes that could or might need to be commented. This will
    modify any nodes in place.
    """
    tu = cursor.tu
    start = cursor.extent.start
    for child in children:
        if child.kind not in UNDOCUMENTED_NODES:
            start = child.extent.end
            continue

        # This may not be 100% accurate but move the start back to the previous
        # line. This solves problems like macro defintions not including the
        # preprocessor `#define` tokens.
        location = child.extent.start
        end = cindex.SourceLocation.from_position(tu, location.file,
                                                  location.line - 1, 1)

        extent = cindex.SourceRange.from_locations(start, end)
        tokens = list(cindex.TokenGroup.get_tokens(tu, extent=extent))

        start = child.extent.end

        if not tokens:
            continue

        token = tokens[-1]
        if token.kind == cindex.TokenKind.COMMENT:
            if token.spelling.startswith(DOCUMENTATION_COMMENT_START):
                child.raw_comment = token.spelling

    first_child = children[0] if children else None
    cursor.raw_comment = get_root_comment(cursor, first_child)


def parse_comment(comment):
    """
    Clean up a C comment such that it no longer has leading `/**`, leading lines
    of `*` or trailing `*/`

    Args:
        comment (str): A c comment.

    Returns:
        str: The comment with the c comment syntax removed.
    """
    # Happens when there is no documentation comment in the source file for the
    # item.
    if comment is None:
        return ''

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
    contents = re.sub(r'^\s?\*/?|^/\*+<?|\*+/', lambda x: len(x.group(0)) * ' ',
                      comment, flags=re.MULTILINE)

    # Dedent doesn't work with carriage returns, \r
    contents = contents.replace('\r\n', '\n')
    contents = textwrap.dedent(contents)

    # there may still be left over newlines so only strip those but leave any
    # whitespaces.
    contents = contents.strip('\n')

    return contents

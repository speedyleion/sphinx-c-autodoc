"""
Load the c file objects
"""

import json
import os
import re
import textwrap

from itertools import dropwhile
from collections import OrderedDict

from bs4 import BeautifulSoup
from clang import cindex

from c_docs.clang.patches import patch_clang

# Must do this prior to calling into clang
patch_clang()


class DocumentedObject:
    """
    A representation of a loaded c file focusing on the documentation of the
    elements.

    Attributes:
        type (str): The type of this item one of
    """
    _type = 'object'

    def __init__(self):
        self.doc = ''
        self.name = ''
        self.node = None
        self.type = self._type
        self._children = None
        self._soup = None

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
        return self.name

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
        return self.doc

    @property
    def soup(self):
        """
        Get the beautifulsoup representation of this object's comment.

        Returns:
            BeautifulSoup: The xml comment for this C object turned into soup.
        """
        if self._soup is None:
            comment = self.node.getParsedComment().as_xml()
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


class DocumentedMember(DocumentedObject):
    """
    A documented file
    """
    _type = 'member'

    def format_name(self) -> str:
        """Format the name of *self.object*.

        This normally should be something that can be parsed by the generated
        directive, but doesn't need to be (Sphinx will display it unparsed
        then).

        For things like functions and others this will include the return type.
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
        root = self.soup.contents[0]
        if root.find('parameters', recursive=False) or root.find('resultdiscussion'):
            return self.get_soup_doc()

        return self.doc

    def format_args(self, **kwargs) -> str:
        """
        Creates the parenthesis version of the function signature.  i.e. this
        will be the `(int hello, int what)` portion of the header.
        """
        root = self.soup.contents[0]
        decl = root.find('declaration')
        _, args = decl.text.split('(', 1)
        return '(' + args

    def format_name(self) -> str:
        """Format the name of *self.object*.

        This normally should be something that can be parsed by the generated
        directive, but doesn't need to be (Sphinx will display it unparsed
        then).

        For things like functions and others this will include the return type.
        """
        root = self.soup.contents[0]
        decl = root.find('declaration')
        name, _ = decl.text.split('(', 1)
        return name


class DocumentedType(DocumentedObject):
    """
    A documented type(def)
    """
    _type = 'type'

    def format_name(self) -> str:
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

    def format_name(self) -> str:
        """Format the name of *self.object*.

        This normally should be something that can be parsed by the generated
        directive, but doesn't need to be (Sphinx will display it unparsed
        then).

        For things like functions and others this will include the return type.
        """
        return f'{self._type} {self.name}'

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
                self._children[member.spelling] = object_from_cursor(member)

        return self._children


class DocumentedUnion(DocumentedStructure):
    """
    Class for unions
    """
    _type = 'union'


CURSORKIND_TO_OBJECT_CLASS = {cindex.CursorKind.TRANSLATION_UNIT: DocumentedFile,
                              cindex.CursorKind.FUNCTION_DECL: DocumentedFunction,
                              cindex.CursorKind.STRUCT_DECL: DocumentedStructure,
                              cindex.CursorKind.UNION_DECL: DocumentedUnion,
                              cindex.CursorKind.FIELD_DECL: DocumentedMember,
                              cindex.CursorKind.TYPEDEF_DECL: DocumentedType}


def object_from_cursor(cursor):
    """
    Create an instance from a :class:`cindex.Cursor`
    """
    # Spelling is always good on the "primary" node.
    name = cursor.spelling

    # Don't document anonymouse items
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
    if cursor.kind in (cindex.CursorKind.TYPEDEF_DECL,):
        try:
            underlying_node = next(cursor.get_children())
            if underlying_node.kind in (cindex.CursorKind.STRUCT_DECL,):
                return underlying_node
        except StopIteration:
            # No children for typedefs of native types, i.e. `typedef int some_int;`
            pass

    return cursor


def get_file_comment(cursor):
    """
    Get's the comment at the top of the file
    """
    try:
        token = next(cursor.get_tokens())
    except StopIteration:
        # Only happens with a completely empty file
        return ''

    if token.kind == cindex.TokenKind.COMMENT:
        try:
            node = next(cursor.get_children())
            node_comment = node.raw_comment
        except StopIteration:
            node_comment = ''

        # When the first comment is for the first node then the file lacks a
        # dedicated comment.
        if node_comment != token.spelling:
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

    tu = cindex.TranslationUnit.from_source(filename)
    cursor = tu.cursor

    root_document = DocumentedFile()
    root_document.doc = get_file_comment(cursor)
    root_document.name = os.path.basename(cursor.spelling)

    # Skip past all the nodes that show up due to the includes as well as the
    # compiler provided ones.
    node_iter = dropwhile(lambda x: not x.location.isFromMainFile(),
                          cursor.get_children())

    # TODO need to consider a better way to build this up, taking the
    # dictionary and modifying in place isn't ideal.
    children = root_document.children
    for node in node_iter:
        item = object_from_cursor(node)
        if item:
            children[item.name] = item

    return root_document


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

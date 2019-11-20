"""
Parser of c files
"""

import json
import os
import textwrap

from itertools import dropwhile
from collections import OrderedDict

from clang import cindex

CURSORKIND_TO_ITEM_TYPES = {cindex.CursorKind.TRANSLATION_UNIT: 'file',
                            cindex.CursorKind.FUNCTION_DECL: 'function',
                            cindex.CursorKind.STRUCT_DECL: 'struct',
                            cindex.CursorKind.TYPEDEF_DECL: 'type'}


class DocumentedItem:
    """
    A representation of a parsed c file focusing on the documentation of the
    elements.

    Attributes:
        type (str): The type of this item one of
    """
    def __init__(self):
        self.doc = ''
        self.type = ''
        self.name = ''
        self.children = OrderedDict()

    @classmethod
    def from_cursor(cls, cursor):
        """
        Create an instance from a :class:`cindex.Cursor`
        """
        doc = cls()

        # Spelling is always good on the "primary" node.
        doc.name = cursor.spelling

        nested_cursor = get_nested_node(cursor)
        doc.doc = parse_comment(nested_cursor.raw_comment)
        doc.type = CURSORKIND_TO_ITEM_TYPES[nested_cursor.kind]

        if doc.doc and doc.name:
            return doc

        return None

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


def get_nested_node(cursor):
    """
    Retrieve the nested node that `cursor` may be shadowing
    """
    if cursor.kind in (cindex.CursorKind.TYPEDEF_DECL,):
        underlying_node = next(cursor.get_children())
        if underlying_node.kind in (cindex.CursorKind.STRUCT_DECL,):
            return underlying_node

    return cursor


def get_file_comment(cursor):
    """
    Get's the comment at the top of the file
    """
    token = next(cursor.get_tokens())

    # TODO look for being attached to a cursor or maybe just look for comment
    # being the first line...
    if token.kind == cindex.TokenKind.COMMENT:
        return parse_comment(token.spelling)

    return ''


def parse(filename):
    """
    Parse a C file into a tree of :class:`DocumentedItem`\'s

    Args:
        filename (str): The c file to parse into a documented item

    Returns:
        :class:`DocumentedItem`: The documented version of `filename`.

    """

    tu = cindex.TranslationUnit.from_source(filename)
    cursor = tu.cursor

    root_document = DocumentedItem()
    root_document.doc = get_file_comment(cursor)
    root_document.type = CURSORKIND_TO_ITEM_TYPES[cursor.kind]
    root_document.name = os.path.basename(cursor.spelling)

    # Skip past all the nodes that show up due to the includes as well as the
    # compiler provided ones.
    node_iter = dropwhile(lambda x: not x.location.isFromMainFile(),
                          cursor.get_children())

    for node in node_iter:
        item = DocumentedItem.from_cursor(node)
        if item:
            root_document.children[item.name] = item

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
    if not comment:
        return ''

    # Remove leading and trailing blocks, needs to be more logical
    comment = comment.splitlines()[1:-1]

    # Remove any leading '*'s
    comment = [c.lstrip('*') for c in comment]

    comment = '\n'.join(comment).strip()

    return textwrap.dedent(comment)


# pylint: disable=invalid-name
def SourceLocation_isFromMainFile(self):
    """
    Tests if a :class:`cindex.SourceLocation` is in the main translation unit
    being parsed.

    Returns:
        bool: True if this location is in the main file of the translation unit.
            False otherwise.
    """
    return cindex.conf.lib.clang_Location_isFromMainFile(self)


# List of functions which are in the native libclang but aren't normally
# provided by the python bindings of clang.
FUNCTION_LIST = [
    ('clang_Location_isFromMainFile', [cindex.SourceLocation], bool),
]


def patch_cindex():
    """
    This will patch the variables and classes in cindex to provide more
    functionality than usual.

    Monkeypatching is utilized so that people can more easily upgrade the
    libclang version with its cindex file and not have to merge it.
    """
    # Create a sequence of all of the currently known function names in cindex.
    known_names = tuple(f[0] for f in cindex.functionList)

    # Add any unknown versions in
    for func in FUNCTION_LIST:
        if func[0] not in known_names:
            cindex.functionList.append(func)

    cindex.SourceLocation.isFromMainFile = SourceLocation_isFromMainFile


# Must do this prior to calling into clang
patch_cindex()

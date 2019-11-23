"""
Parser of c files
"""

import json
import os
import re
import textwrap

from itertools import dropwhile
from collections import OrderedDict

from clang import cindex


class DocumentedObject:
    """
    A representation of a parsed c file focusing on the documentation of the
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
        self.children = OrderedDict()

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


class DocumentedFile(DocumentedObject):
    """
    A documented file
    """
    _type = 'file'


class DocumentedStructure(DocumentedObject):
    """
    A documented structure
    """
    _type = 'struct'


class DocumentedType(DocumentedObject):
    """
    A documented type(def)
    """
    _type = 'type'


class DocumentedFunction(DocumentedObject):
    """
    A function specific documented object.
    """
    _type = 'function'

    def format_args(self, **kwargs) -> str:
        """
        Creates the parenthesis version of the function signature.  i.e. this
        will be the `(int hello, int what)` portion of the header.
        """
        func = self.node
        args = []
        for arg in func.get_arguments():
            args.append(' '.join(t.spelling for t in arg.get_tokens()))

        if not args:
            args = ['void']

        return '({})'.format(', '.join(args))

    def format_name(self) -> str:
        """Format the name of *self.object*.

        This normally should be something that can be parsed by the generated
        directive, but doesn't need to be (Sphinx will display it unparsed
        then).

        For things like functions and others this will include the return type.
        """
        func = self.node

        # The Cursor kinds have translation units as protected, underscore, but
        # one can't do very much querying without access to the translation unit
        tu = func._tu  # pylint: disable=protected-access

        # For functions the extent encompasses the return value, and the
        # location is the beginning of the functions name.  So we can consume
        # all tokens in between.
        end = cindex.SourceLocation.from_offset(tu, func.location.file,
                                                func.location.offset - 1)
        extent = cindex.SourceRange.from_locations(func.extent.start, end)

        return_type = ' '.join(t.spelling for t in
                               cindex.TokenGroup.get_tokens(tu, extent=extent))

        return '{} {}'.format(return_type, func.spelling)


CURSORKIND_TO_OBJECT_CLASS = {cindex.CursorKind.TRANSLATION_UNIT: DocumentedFile,
                              cindex.CursorKind.FUNCTION_DECL: DocumentedFunction,
                              cindex.CursorKind.STRUCT_DECL: DocumentedStructure,
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
    class_ = CURSORKIND_TO_OBJECT_CLASS[nested_cursor.kind]
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


def parse(filename):
    """
    Parse a C file into a tree of :class:`DocumentedObject`\'s

    Args:
        filename (str): The c file to parse into a documented item

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

    for node in node_iter:
        item = object_from_cursor(node)
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
    # Happens when there is no documentation comment in the source file for the
    # item.
    if comment is None:
        return ''

    # Notes on the regex here.
    #   Option 1 '\s?\*/?'
    #       This piece will match comment lines that start with '*' or ' *'.
    #       This will also match a trailing '*/' for the end of a comment
    #
    #   Option 2 '^/\*+'
    #       This will match the start of a comment '/*' and consume any
    #       subsequent '*'.
    #
    #   Option 3 '\*+/'
    #       Matches any and all '*' up to the end of the comment string.
    contents = re.sub(r'^\s?\*/?|^/\*+|\*+/', lambda x: len(x.group(0)) * ' ',
                      comment, flags=re.MULTILINE)

    # Dedent doesn't work with carriage returns, \r
    contents = contents.replace('\r\n', '\n')
    contents = textwrap.dedent(contents)

    # there may still be left over newlines so only strip those but leave any
    # whitespaces.
    contents = contents.strip('\n')

    return contents


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

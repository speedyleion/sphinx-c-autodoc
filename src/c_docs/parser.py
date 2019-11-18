"""
Parser of c files
"""

import json
import textwrap
from clang import cindex
from itertools import chain, dropwhile

class DocumentedItem:
    """
    A representation of a parsed c file focusing on the documentation of the
    elements.
    """
    def __init__(self):
        self.doc = ''
        self.children = []

    def __str__(self):
        """
        Will turn this instance into a JSON like representation.
        """
        obj_dict = {}
        obj_dict['doc'] = self.doc
        if self.children:
            obj_dict['children'] = []
            for c in self.children:
                obj_dict['children'].append(json.loads(str(c)))

        return json.dumps(obj_dict)

def get_file_comment(cursor):
    """
    """
    token = next(cursor.get_tokens())

    # TODO look for being attached to a cursor
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
    root_document = DocumentedItem()

    tu = cindex.TranslationUnit.from_source(filename)
    cursor = tu.cursor
                          
    root_document.doc = get_file_comment(cursor)
    
    # Skip past all the nodes that show up due to the includes as well as the
    # compiler provided ones.
    node_iter = dropwhile(lambda x: not x.location.isFromMainFile(),
                          cursor.get_children())

    for n in node_iter:
        if n.raw_comment:
            item = DocumentedItem()
            item.doc = parse_comment(n.raw_comment)
            root_document.children.append(item)

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
    # Remove leading and trailing blocks, needs to be more logical
    comment = comment.splitlines()[1:-1]

    # Remove any leading '*'s
    comment = [c.lstrip('*') for c in comment]

    comment = '\n'.join(comment).strip()

    return textwrap.dedent(comment)


def SourceLocation_isFromMainFile(self):
    """
    Tests if a :class:`cindex.SourceLocation` is in the main translation unit being parsed.

    Returns:
        bool: True if this location is in the main file of the translation unit.  False
              otherwise.
    """
    return cindex.conf.lib.clang_Location_isFromMainFile(self)


# List of functions which are in the native libclang but aren't normally
# provided by the python bindings of clang.
functionList = [
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
    for f in functionList:
        if f[0] not in known_names:
            cindex.functionList.append(f)

    cindex.SourceLocation.isFromMainFile = SourceLocation_isFromMainFile

# Must do this prior to calling into clang
patch_cindex()



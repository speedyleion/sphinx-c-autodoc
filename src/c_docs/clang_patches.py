"""
Provide functionality to patch the python clang bindings for some missing
functionality.

pylint invalid-name: This is being disabled because the methods are using the
c style object nameing convetion of <ClassName>_<methodName>. The
class name is in title case, matching the python convention for classes. The
method names are in camel case, matching the cindex method name conventions.
"""
# pylint: disable=invalid-name

import ctypes

from clang import cindex


def SourceLocation_isFromMainFile(self):
    """
    Tests if a :class:`cindex.SourceLocation` is in the main translation unit
    being parsed.

    Returns:
        bool: True if this location is in the main file of the translation unit.
            False otherwise.
    """
    return cindex.conf.lib.clang_Location_isFromMainFile(self)


def Cursor_getParsedComment(self):
    """
    Get the parsed comment for the cursor

    Returns:
        Comment: The comment for the cursor
    """
    return cindex.conf.lib.clang_Cursor_getParsedComment(self)


# pylint: disable=too-few-public-methods
class Comment(ctypes.Structure):
    """
    A CXComment from clang
    """
    _fields_ = [("node", ctypes.c_void_p),
                ("tu", ctypes.POINTER(ctypes.c_void_p))]

    def as_XML(self):
        """
        Return this comment as an xml string
        """
        return cindex.conf.lib.clang_FullComment_getAsXML(self)


# List of functions which are in the native libclang but aren't normally
# provided by the python bindings of clang.
# pylint: disable=protected-access
FUNCTION_LIST = [
    ('clang_Location_isFromMainFile', [cindex.SourceLocation], bool),
    ('clang_FullComment_getAsXML', [Comment], cindex._CXString,
     cindex._CXString.from_result),
    ('clang_Cursor_getParsedComment', [cindex.Cursor], Comment),
]


def patch_clang():
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
    cindex.Cursor.getParsedComment = Cursor_getParsedComment

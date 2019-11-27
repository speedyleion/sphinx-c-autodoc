"""
Provide functionality to patch the python clang bindings for some missing
functionality.

pylint invalid-name: This is being disabled because the methods are using the
c style object nameing convetion of <ClassName>_<methodName>. The
class name is in title case, matching the python convention for classes. The
method names are in camel case, matching the cindex method name conventions.
"""
# pylint: disable=invalid-name

from clang import cindex

from c_docs.clang.comments import Comment


def SourceLocation_isFromMainFile(self):
    """
    Tests if a :class:`cindex.SourceLocation` is in the main translation unit
    being parsed.

    Returns:
        bool: True if this location is in the main file of the translation unit.
            False otherwise.
    """
    return cindex.conf.lib.clang_Location_isFromMainFile(self)


def Cursor_is_macro_function_like(self):
    """
    Determine if the macro is a function like macro

    Returns:
        boo: True if the macro is function like
    """
    return cindex.conf.lib.clang_Cursor_isMacroFunctionLike(self)


def Cursor_getParsedComment(self):
    """
    Get the parsed comment for the cursor

    Returns:
        Comment: The comment for the cursor
    """
    return cindex.conf.lib.clang_Cursor_getParsedComment(self)


def Cursor_cached_raw_comment(self):
    """
    Provides a caching mechanism to a Cursor's raw comment instead of looking
    it up each time it's called.
    """
    if self._raw_comment is None:
        self._raw_comment = cindex.conf.lib.clang_Cursor_getRawCommentText(self)

    return self._raw_comment


def Cursor_set_raw_comment(self, value):
    """
    Provides a mechanism to a set a Cursor's raw comment. For things like
    macros clang doesn't provide a mechanism to associate comments. So it may
    be done later, but the cursors can still be passed around like normal.
    """
    self._raw_comment = value


def Cursor_tu(self):
    """
    Provide the cursor's translation unit in a "public"
    The Cursors have translation units as protected, underscore, but one
    can't do very much querying without access to the translation unit.
    """
    return self._tu


# List of functions which are in the native libclang but aren't normally
# provided by the python bindings of clang.
# pylint: disable=protected-access
FUNCTION_LIST = [
    ('clang_Location_isFromMainFile', [cindex.SourceLocation], bool),
    ('clang_Cursor_isMacroFunctionLike', [cindex.Cursor], bool),
    ('clang_Cursor_getParsedComment', [cindex.Cursor], Comment),
    ('clang_FullComment_getAsXML', [Comment], cindex._CXString,
     cindex._CXString.from_result),
]


def patch_clang():
    """
    This will patch the variables and classes in cindex to provide more
    functionality than usual as well as make some things a little more
    pythonic.
    """
    add_dll_entry_points()

    add_new_methods()

    override_methods()


def override_methods():
    """
    Override some methods and properties in the bindings to make them more
    pythonic and or more efficient.
    """
    cindex.Cursor._raw_comment = None
    cindex.Cursor.raw_comment = property(Cursor_cached_raw_comment).setter(Cursor_set_raw_comment)


def add_new_methods():
    """
    Add new methods to the classes in clang.
    """
    cindex.SourceLocation.isFromMainFile = SourceLocation_isFromMainFile
    cindex.Cursor.getParsedComment = Cursor_getParsedComment
    cindex.Cursor.is_macro_function_like = Cursor_is_macro_function_like
    cindex.Cursor.tu = property(Cursor_tu)


def add_dll_entry_points():
    """
    Add functions available in the clang dll but not listed in the python
    clang bindings.
    """
    # Create a sequence of all of the currently known function names in cindex.
    known_names = tuple(f[0] for f in cindex.functionList)

    # Add any unknown versions in
    for func in FUNCTION_LIST:
        if func[0] not in known_names:
            cindex.functionList.append(func)

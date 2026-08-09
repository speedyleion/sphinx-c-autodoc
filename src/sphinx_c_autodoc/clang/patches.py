"""
Provide functionality to patch the python clang bindings for some missing
functionality.

"""

# This module deliberately accesses private cindex members while containing the
# monkey-patching in one place for other consumers.

from typing import Any, List, Optional, Tuple, cast

from clang import cindex
from clang.cindex import Cursor, SourceLocation, SourceRange, TranslationUnit

from sphinx_c_autodoc.clang.comments import Comment, cxstring_to_str


def source_location_is_from_main_file(self: SourceLocation) -> bool:
    """
    Tests if a :class:`cindex.SourceLocation` is in the main translation unit
    being parsed.

    Returns:
        bool: True if this location is in the main file of the translation unit.
            False otherwise.
    """
    return cindex.conf.lib.clang_Location_isFromMainFile(self)


def cursor_is_macro_function_like(self: Cursor) -> bool:
    """
    Determine if the macro is a function like macro

    Returns:
        boo: True if the macro is function like
    """
    return cindex.conf.lib.clang_Cursor_isMacroFunctionLike(self)


def cursor_get_parsed_comment(self: Cursor) -> Comment:
    """
    Get the parsed comment for the cursor

    Returns:
        Comment: The comment for the cursor
    """
    return cindex.conf.lib.clang_Cursor_getParsedComment(self)


def cursor_comment_extent(self: Cursor) -> SourceRange:
    """
    Gets the extent of the associated comment.

    For some reason libclang calls this "range" while other parts of the
    interface use the term "extent", for consistency with the python API
    naming extent was used here.

    Returns:
        cindex.SourceRange: The extent for the cursor's raw_comment.
    """
    if self._comment_extent is None:
        self._comment_extent = cindex.conf.lib.clang_Cursor_getCommentRange(self)

    return self._comment_extent


def cursor_set_comment_extent(self: Cursor, value: SourceRange) -> None:
    """
    Provides a mechanism to a set a Cursor's comment extent. For things like
    macros clang doesn't provide a mechanism to associate comments. So it may
    be done later, but the cursors can still be passed around like normal.
    """
    self._comment_extent = value


def cursor_cached_raw_comment(self: Cursor) -> Optional[str]:
    """
    Provides a caching mechanism to a Cursor's raw comment instead of looking
    it up each time it's called.
    """
    if self._raw_comment is None:
        self._raw_comment = cxstring_to_str(
            cindex.conf.lib.clang_Cursor_getRawCommentText(self)
        )

    return self._raw_comment


def cursor_set_raw_comment(self: Cursor, value: str) -> None:
    """
    Provides a mechanism to a set a Cursor's raw comment. For things like
    macros clang doesn't provide a mechanism to associate comments. So it may
    be done later, but the cursors can still be passed around like normal.
    """
    self._raw_comment = value


def cursor_tu(self: Cursor) -> TranslationUnit:
    """
    Provide the cursor's translation unit in a "public"
    The Cursors have translation units as protected, underscore, but one
    can't do very much querying without access to the translation unit.
    """
    return self._tu


# List of functions which are in the native libclang but aren't normally
# provided by the python bindings of clang.
FUNCTION_LIST: List[Tuple] = [
    ("clang_Location_isFromMainFile", [cindex.SourceLocation], bool),
    ("clang_Cursor_isMacroFunctionLike", [cindex.Cursor], bool),
    ("clang_Cursor_getCommentRange", [cindex.Cursor], cindex.SourceRange),
    ("clang_Cursor_getParsedComment", [cindex.Cursor], Comment),
    (
        "clang_FullComment_getAsXML",
        [Comment],
        cindex._CXString,
    ),
]


def patch_clang() -> None:
    """
    This will patch the variables and classes in cindex to provide more
    functionality than usual as well as make some things a little more
    pythonic.
    """
    add_dll_entry_points()

    add_new_methods()

    override_methods()


def override_methods() -> None:
    """
    Override some methods and properties in the bindings to make them more
    pythonic and or more efficient.
    """
    cursor_class = cast(Any, cindex.Cursor)
    cursor_class._raw_comment = None
    cursor_class.raw_comment = property(cursor_cached_raw_comment).setter(
        cursor_set_raw_comment
    )


def add_new_methods() -> None:
    """
    Add new methods to the classes in clang.
    """
    source_location_class = cast(Any, cindex.SourceLocation)
    source_location_class.isFromMainFile = source_location_is_from_main_file

    cursor_class = cast(Any, cindex.Cursor)
    cursor_class._comment_extent = None
    cursor_class.comment_extent = property(cursor_comment_extent).setter(
        cursor_set_comment_extent
    )
    cursor_class.getParsedComment = cursor_get_parsed_comment
    cursor_class.is_macro_function_like = cursor_is_macro_function_like
    cursor_class.tu = property(cursor_tu)


def add_dll_entry_points() -> None:
    """
    Add functions available in the clang dll but not listed in the python
    clang bindings.
    """
    cindex_list = getattr(cindex, "FUNCTION_LIST", None)
    # the function list was named `functionList` in clang 20 and before
    if cindex_list is None:  # pragma: no cover
        cindex_list = cast(Any, cindex).functionList
    # Create a sequence of all of the currently known function names in cindex.
    known_names = tuple(f[0] for f in cindex_list)

    # Add any unknown versions in
    for func in FUNCTION_LIST:
        if func[0] not in known_names:
            cindex_list.append(func)

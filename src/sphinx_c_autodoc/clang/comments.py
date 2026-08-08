"""
Expose some CXComment functionality to python for libclang

"""

import ctypes

from typing import Any, Optional

from clang import cindex


# Access is necessary because clang does not expose a public CXString converter.
# pylint: disable=protected-access
def cxstring_to_str(value: Any) -> Optional[str]:
    """Convert a CXString unless the clang bindings already converted it."""
    if isinstance(value, cindex._CXString):
        return cindex._CXString.from_result(value)
    return value


# pylint: disable=too-few-public-methods
class Comment(ctypes.Structure):
    """
    A CXComment from clang
    """

    _fields_ = [("node", ctypes.c_void_p), ("tu", ctypes.POINTER(ctypes.c_void_p))]

    def as_xml(self) -> Optional[str]:
        """
        Return this comment as an xml string
        """
        full_comment = cxstring_to_str(cindex.conf.lib.clang_FullComment_getAsXML(self))
        # Clang 21 and up return empty string '', instead of None
        # Keeping at callers logic to look for None until Clang 21 is min Clang version
        return full_comment or None

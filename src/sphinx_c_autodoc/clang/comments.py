"""
Expose some CXComment functionality to python for libclang

"""
import ctypes

from typing import Optional

from clang import cindex


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
        return cindex.conf.lib.clang_FullComment_getAsXML(self)

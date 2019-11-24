"""
Expose the CXComment functionality to python for libclang

The CXComments from libclang are built up into a tree like structure, which
does not directly relate to the actual source codes tree like structure.

For example a function comment of the form:

.. code-block:: c

    /**
     * This is the description of some function
     * It contains multiple lines of text
     *
     * Here is a new paragraph as someone would interpret
     * from a markdown style syntax
     *
     * @param foo A parameter with no direction
     * @param [in] bar A parameter with an `in` direction
     *
     * @returns
     *     Some interesting value
     */

Would be broken up into the following tree like structure::

                                        FULL_COMMENT
                                             |
          +----------+----------+------------+-------------+----------+-----------+
          |          |          |            |             |          |           |
          v          v          v            v             v          v           v
      PARAGRAPH  PARAGRAPH  PARAGRAPH PARAM_COMMAND PARAM_COMMAND PARAGRAPH BLOCK_COMMAND
          |          |          |            |             |          |           |
       +--+--+    +--+--+       |            |             |          |           |
       |     |    |     |       |            |             |          |           |
       v     v    v     v       v            v             v          |           |
     TEXT   TEXT TEXT TEXT     TEXT      PARAGRAPH     PARAGRAPH    TEXT      PARAGRAPH
       |     |    |     |       |            |             |          |           |
       v     |    |     |       |            |             |          |           |
    " This is the description of some function"            |          |           |
             |    |     |       |            |             |          |           |
             v    |     |       |            |             |          |           |
    " It contains multiple lines of text"    |             |          |           |
                  |     |       |            |             |          |           |
                  v     |       |            |             |          |           |
    " Here is a new paragraph as someone would interpret"  |          |           |
                        |       |            |             |          |           |
                        v       |            |             |          |           |
    " from a markdown style syntax"          |             |          |           |
                                |            |             |          |           |
                                v            |             |          |           |
                               " "           |             |          |           |
                                          +--+--+          |          |           |
                                          |     |          |          |           |
                                          v     v          v          |           v
                                        TEXT   TEXT       TEXT        |          TEXT
                                          |     |          |          |           |
                                          v     |          |          |           |
             " A parameter with no direction"   |          |          |           |
                                                v          |          |           |
                                               " "         |          |           |
                                                           v          |           |
                         " A parameter with an `in` direction"        |           |
                                                                      v           |
                                                                     " "          |
                                                                                  v
                                                        "     Some interesting value"





"""
import ctypes
from clang import cindex


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

    def get_num_children(self):
        """
        Return the number of child comments???
        """
        return cindex.conf.lib.clang_Comment_getNumChildren(self)

    def get_children(self):
        """
        Iterates through the child comments
        """
        for i in range(cindex.conf.lib.clang_Comment_getNumChildren(self)):
            yield cindex.conf.lib.clang_Comment_getChild(self, i)

    @property
    def kind(self):
        """Return the kind of this comment."""
        return CommentKind.from_id(cindex.conf.lib.clang_Comment_getKind(self))

    def get_text(self):
        """
        Yes
        """
        return cindex.conf.lib.clang_TextComment_getText(self)

    def is_whitespace(self):
        """
        Sure
        """
        return cindex.conf.lib.clang_Comment_isWhitespace(self) != 0

class CommentKind(cindex.BaseEnumeration):
    """
    A CommentKind describes the kind of entity that a Comment points to.
    """

    # The required BaseEnumeration declarations.
    _kinds = []
    _name_map = None

    def __repr__(self):
        return 'CommentKind.%s' % (self.name,)

CommentKind.NULL = CommentKind(0)
CommentKind.TEXT = CommentKind(1)
CommentKind.INLINE_COMMAND = CommentKind(2)
CommentKind.HTML_START_TAG = CommentKind(3)
CommentKind.HTML_START_TAG = CommentKind(4)
CommentKind.PARAGRAPH = CommentKind(5)
CommentKind.BLOCK_COMMAND = CommentKind(6)
CommentKind.PARAM_COMMAND = CommentKind(7)
CommentKind.TEMPLATE_PARAM_COMMAND = CommentKind(8)
CommentKind.VERBATIM_BLOCK_COMMAND = CommentKind(9)
CommentKind.VERBATIM_BLOCK_LINE = CommentKind(10)
CommentKind.VERBATIM_LINE = CommentKind(11)
CommentKind.FULL_COMMENT = CommentKind(12)

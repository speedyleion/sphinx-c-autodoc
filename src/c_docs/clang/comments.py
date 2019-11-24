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

    _kind = None

    def as_xml(self):
        """
        Return this comment as an xml string
        """
        return cindex.conf.lib.clang_FullComment_getAsXML(self)

    def get_children(self):
        """
        Iterates through the child comments.

        Yields:
            Comment: The children
        """
        for i in range(cindex.conf.lib.clang_Comment_getNumChildren(self)):
            yield cindex.conf.lib.clang_Comment_getChild(self, i)

    @property
    def kind(self):
        """Return the kind of this comment."""
        if self._kind is None:
            self._kind = CommentKind.from_id(cindex.conf.lib.clang_Comment_getKind(self))

        return self._kind

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

# Null comment.  No AST node is constructed at the requested location
# because there is no text or a syntax error.
CommentKind.NULL = CommentKind(0)

# Plain text.  Inline content.
CommentKind.TEXT = CommentKind(1)

# A command with word-like arguments that is considered inline content.
#
# For example: \\c command.
CommentKind.INLINE_COMMAND = CommentKind(2)

# HTML start tag with attributes (name-value pairs).  Considered
# inline content.
#
# For example::
#
#   <br> <br /> <a href="http://example.org/">
#
CommentKind.HTML_START_TAG = CommentKind(3)

# HTML end tag.  Considered inline content.
#
# For example::
#
#   </a>
#
CommentKind.HTML_START_TAG = CommentKind(4)

# A paragraph, contains inline comment.  The paragraph itself is
# block content.
CommentKind.PARAGRAPH = CommentKind(5)

# A command that has zero or more word-like arguments (number of
# word-like arguments depends on command name) and a paragraph as an
# argument.  Block command is block content.
#
# Paragraph argument is also a child of the block command.
#
# For example: \has 0 word-like arguments and a paragraph argument.
#
# AST nodes of special kinds that parser knows about (e. g., \\param
# command) have their own node kinds.
CommentKind.BLOCK_COMMAND = CommentKind(6)

# A \\param or \\arg command that describes the function parameter
# (name, passing direction, description).
#
# For example: \\param [in] ParamName description.
CommentKind.PARAM_COMMAND = CommentKind(7)

# A \\tparam command that describes a template parameter (name and
# description).
#
# For example: \\tparam T description.
CommentKind.TEMPLATE_PARAM_COMMAND = CommentKind(8)

# A verbatim block command (e. g., preformatted code).  Verbatim
# block has an opening and a closing command and contains multiple lines of
# text (\c CXComment_VerbatimBlockLine child nodes).
#
# For example::
#
#   \\verbatim
#   aaa
#   \\endverbatim
#
CommentKind.VERBATIM_BLOCK_COMMAND = CommentKind(9)

# A line of text that is contained within a
# CXComment_VerbatimBlockCommand node.
CommentKind.VERBATIM_BLOCK_LINE = CommentKind(10)

# A verbatim line command.  Verbatim line has an opening command,
# a single line of text (up to the newline after the opening command) and
# has no closing command.
CommentKind.VERBATIM_LINE = CommentKind(11)


# A full comment attached to a declaration, contains block content.
CommentKind.FULL_COMMENT = CommentKind(12)

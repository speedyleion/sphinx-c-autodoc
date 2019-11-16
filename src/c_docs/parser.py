"""
Parser of c files
"""

import textwrap
from clang import cindex

def parse(filename):
    """
    """
    cursor = cindex.TranslationUnit.from_source(filename)
    
    # HACK Just to get tests passing re-work later
    comments = []
    for t in cursor.get_tokens():
        if t.kind != clang.cindex.TokenKind.Comment:
            continue

        comments.appned(parse_comment(t.spelling))

    return comments

def parse_comment(comment):
    """
    """
    # Remove leading and trailing blocks, needs to be more logical
    comment = comment.splitlines[1:-1]

    # Remove any leading '*'s
    #???

    comment = '\n'.join(comment).strip()

    return textwrap.dedent(comment)

"""
Parser of c files
"""

import textwrap
from clang import cindex

def parse(filename):
    """
    """
    tu = cindex.TranslationUnit.from_source(filename)
    cursor = tu.cursor

    # HACK Just to get tests passing re-work later
    comments = []
    for t in cursor.get_tokens():
        if t.kind != cindex.TokenKind.COMMENT:
            continue

        comments.append(parse_comment(t.spelling))

    return comments

def parse_comment(comment):
    """
    """
    # Remove leading and trailing blocks, needs to be more logical
    comment = comment.splitlines()[1:-1]

    # Remove any leading '*'s
    comment = [c.lstrip('*') for c in comment]

    comment = '\n'.join(comment).strip()

    return textwrap.dedent(comment)

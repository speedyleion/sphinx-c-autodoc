Developer Notes
===============

Common Terms
------------

Construct:
    In order to find a common word to describe things such as C functions, C
    types, C struct members a common term is needed. This common term is
    _construct_.

AST:
    Abstract Syntax Tree or AST is a common term used to describe the break
    down of a C source file into its components. Normally an AST goes all the
    way down to things like if conditions and other constructs. However for
    the use in autodoc there is no reason to break down the contents of a
    function. Structures, unions and enums are further broken down into their
    member or enumerator constants though.

    For this extension the common AST is just a simple dictionary which has
    the following entries:

        ``name`` (str):
            The name of the construct, i.e. function name, variable
            name etc.

        ``start_line`` (int):
            The line number in the source code where this construct
            starts. Line numbers are 1 based, not 0 based.

        ``end_line`` (int):
            The line number in the source code where this construct
            ends. For some constructs this line will be the same as
            the start. Line numbers are 1 based, not 0 based.

        ``children`` (list):
            A list of child constructs with the same fields as this.
            Children may be things such as struct members. Or
            functions within a file where the file is the root node.
            An empty list is still provided for no children.

    The file itself should be the root node.
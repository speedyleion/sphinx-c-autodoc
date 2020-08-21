Directives
==========

Most C constructs are available as an `autodoc`_ style directive.

Do to the fact that `autodoc`_ directives are set up into a global namespace and
not in `domain`_ specific namespace. The directives used for auto documenting C
constructs will have a ``c`` moniker in their names.

Keeping consistent with `autodoc`_, the term **member** is used generically to
refer to any sub construct of another C construct.  For example in this
documentation any usage a C function may be referred to as a member of a C
module.

Common Options
--------------

.. rst:directive:option:: noindex

By default the documentation instances are added to the index. To prevent an
instance from being added to the index provide this option.

.. rst:directive:: .. autocmodule:: filename

    Create documentation for `filename`. The `filename` is relative to
    :ref:`configuration:c_autodoc_roots`. This directive can be used for both
    C source files as well as C header files.

    The contents of the first documentation comment will be utilized as the
    documentation for `filename`.

    .. rst:directive:option:: members

        Specify which members to recursively document.

        This option has 4 states:

        - Omitted will result in the ``members`` entry of
          `autodoc_default_options`_ being used. If ``members`` is omitted
          from `autodoc_default_options`_ then no members will be
          automatically documented.
        - Specified as ``:no-members:``, no members will be automatically
          documented.
        - Specified with no arguments, ``:members:``, then all supported C
          constructs at the file level will be recursively documented.
        - Specified with a comma separated list of names,
          ``:members: function_a, struct_b``, only the file members specified will
          be recursively documented.

    .. rst:directive:option:: private-members

        Specify if private members are to be documented. Since C doesn't
        actually have a true idea of public and private, the following rules
        are used to determine these characteristics.

        Members are public if:

            - They are in a header file, ends in `.h`. By nature header files are meant to
              be included in other files, thus anything declared there is
              deemed public.
            - They can be visible outside of the compilation unit. These are
              things the linker can get access to. Mainly this means functions
              and variables that are not static.

        Just as for the standard `autodoc`_ options, one can use the negated
        form of ``:no-private-members:`` to selectively turn off this option
        on a per module basis.

.. rst:directive:: .. autocfunction:: filename::function

    Document the function ``function`` from file ``filename``.

    The documentation will first attempt to utilize the output provided by
    clang.  Clang can parse `Doxygen`_ style markup. So if the function
    parameter documentation or the function return value documentation is seen
    in the clang parsing, then the parsed clang documentation will be used.
    Otherwise the raw function comment block will be utilized.

.. rst:directive:: .. autocmacro:: filename::some_define

    Document a C macro.  Both macro constants as well as function like
    macros.

.. rst:directive:: .. autoctype:: filename::typedef

    Document a typedef

.. rst:directive:: .. autocenum:: filename::enum_name

    Document a enum

    .. rst:directive:option:: members

        Specify which members to recursively document.

        This option has 4 states:

        - Omitted will result in the ``members`` entry of
          `autodoc_default_options`_ being used. If ``members`` is omitted
          from `autodoc_default_options`_ then no members will be
          automatically documented.
        - Specified as ``:no-members:``, no members will be automatically
          documented.
        - Specified with no arguments, ``:members:``, then all enumerator
          constants will be documented.
        - Specified with a comma separated list of names,
          ``:members: field_a, field_b``, only the items specified will be
          recursively documented.

.. rst:directive:: .. autocenumerator:: filename::enum_name.enumerator

    Document a enumerator.  One of the constant values of an enum.

.. rst:directive:: .. autocstruct:: filename::struct_name

    Document a struct

    .. rst:directive:option:: members

        Specify which members to recursively document.

        This option has 4 states:

        - Omitted will result in the ``members`` entry of
          `autodoc_default_options`_ being used. If ``members`` is omitted
          from `autodoc_default_options`_ then no members will be
          automatically documented.
        - Specified as ``:no-members:``, no members will be automatically
          documented.
        - Specified with no arguments, ``:members:``, then all fields will be
          recursively documented.
        - Specified with a comma separated list of names,
          ``:members: field_a, field_b``, only the items specified will be
          recursively documented.

.. rst:directive:: .. autocunion:: filename::union_name

    Document a union

    .. rst:directive:option:: members

        Specify which members to recursively document.

        This option has 4 states:

        - Omitted will result in the ``members`` entry of
          `autodoc_default_options`_ being used. If ``members`` is omitted
          from `autodoc_default_options`_ then no members will be
          automatically documented.
        - Specified as ``:no-members:``, no members will be automatically
          documented.
        - Specified with no arguments, ``:members:``, then all fields will be
          recursively documented.
        - Specified with a comma separated list of names,
          ``:members: field_a, field_b``, only the items specified will be
          recursively documented.

.. rst:directive:: .. autocdata:: filename::variable

    Document a file level variable.

.. rst:directive:: .. autocmember:: filename::struct.field

    Document the specified field of a struct or union.

    .. note:: This is one of the overloaded uses of the term **member**. This
        name was used to keep consistent with the `member`_ wording of the
        `C domain`_.

.. _autodoc: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
.. _member: https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#directive-c:member
.. _domain: https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html
.. _C domain: https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#the-c-domain
.. _Sphinx: https://www.sphinx-doc.org/en/master/index.html
.. _Doxygen: http://www.doxygen.nl/
.. _autodoc_default_options: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_default_options
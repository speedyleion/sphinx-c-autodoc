apidoc
======

The `sphinx-c-apidoc` provides a way to generate documentation files for a C directory.
It is meant to fulfill a similar role to the `sphinx-apidoc`_ command for python
packages.

.. autoprogram:: sphinx_c_autodoc.apidoc:get_parser()
    :prog: sphinx-c-apidoc

Generated Documentation Files
-----------------------------

The generated documentation files will follow the same directory structure of the
provide C source directory.

For example:

.. code-block:: text

    a_project
    ├── file_1.h
    ├── file_2.c
    ├── some_dir
    │   ├── another_dir
    │   │   ├── file_3.h
    │   │   └── file_4.c

would result in:

.. code-block:: text

    doc_dir
    ├── files.rst
    ├── file_1_h.rst
    ├── file_2_c.rst
    ├── some_dir
    │   ├── some_dir.rst
    │   ├── another_dir
    │   │   ├── another_dir.rst
    │   │   ├── file_3_h.rst
    │   │   └── file_4_c.rst

Where `a_project` was provided as the ``source_path`` and `doc_dir` was provided as the
``--output-path``.  ``files.rst`` is the root index or table of contents file.  By
default it only contains references to the other documentation files in the same
directory and any index files in sub directories.

``another_dir.rst`` is the index or table of contents file for the directory
`another_dir` it will only contain references the files in that directory as well as
any index files in subsequent sub directories.

Templates
---------

There are three jinja templates that are utilized for generating the documentation
files.  These can be overridden by passing a directory, via the ``--templatedir``
option, containing any of the templates to override.

header.rst.jinja2
^^^^^^^^^^^^^^^^^

Controls the generation of files deemed to be header files, the ``--header-ext``
option.

Will be passed 2 arguments:

    - ``filepath`` The relative path to the file.  For ``file_3.h``, from the example
      above in :ref:`apidoc:Generated Documentation Files`, this would be
      ``some_dir/another_dir/file_3.h``
    - ``filename`` The name of the file, without relative directory. For ``file_3.h``,
      from the example above in :ref:`apidoc:Generated Documentation Files`, this would
      be ``file_3.h``


source.rst.jinja2
^^^^^^^^^^^^^^^^^

Controls the generation of files deemed to be source files, the ``--source-ext``
option.

Will be passed 2 arguments:

    - ``filepath`` The relative path to the file.  For ``file_4.c``, from the example
      above in :ref:`apidoc:Generated Documentation Files`, this would be
      ``some_dir/another_dir/file_4.c``
    - ``filename`` The name of the file, without relative directory. For ``file_4.c``,
      from the example above in :ref:`apidoc:Generated Documentation Files`, this would
      be ``file_4.c``

toc.rst.jinja2
^^^^^^^^^^^^^^

Controls the generation of index or table of contents files.

Will be passed 3 arguments:

    - ``title`` The name of the index file without extension.
    - ``maxdepth`` The ``-d`` option.
    - ``doc_names`` The list of documentation files in the directory as well as those
      in subdirectories.

.. _sphinx-apidoc: https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html

Viewcode
========

.. Adding some c constructs that won't have a valid file available and
   some that won't exist in a file.

.. c:function:: void non_existent_function()
    :module: example.c

    Documntation for a non-existent function. This will show up as
    documentation but won't link to any source as there is none to link to.

.. c:function:: int napoleon_documented_function(int yes, int another_one)
    :module: example.c
    :noindex:

    This is different documentation than would automatically get pulled from
    example.c.

.. c:function:: void function_without_module_reference()

    Documentation for a function that doesn't have a module option.
    :ref:`does not exist` <- make sure that viewcode handles unknown
    references.

.. c:function:: void function_with_non_existent_module()
    :module: does_not_exist.c

    Documentation for a function that calls out a module which doesn't exist.
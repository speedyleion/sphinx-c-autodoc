/**
 * Test file for focusing on function documentation
 */

/** A Single line function comment */
void single_line_function_comment(void)
{
    printf('hello');
}

/**
 * Function with a return value
 */
int return_value_function(void)
{
    return 3;
}

/**
 * Function with multiple parameters
 */
int multiple_parameters(int a, int b)
{
    return a + b;
}

/**
 * Function with sphinx documented parameters
 *
 * :param param1: The first parameter which is on multiple lines
 *      with this being the second line.
 * :param param2: An alternative second parameter
 *
 * :returns: Some return value.
 */
char * sphinx_documented_parameters(int param1, int param2)
{
    return param1 - param2;
}

/**
 * Function with doxygen style documented parameters
 *
 * @param[in] param1 The first parameter which is on multiple lines
 *      with this being the second line.
 * @param[out] param2 An alternative second parameter
 *
 * @returns Some return value.
 */
char * doxy_documented_parameters(int param1, int param2)
{
    return param1 - param2;
}

/**
 * Function with inline doxygen style documented parameters
 *
 * @returns Something better
 */
char * inline_doxy_documented_parameters(
    int foo, /**< The documentation for the foo parameter */
    int baz /**< The documentation for the baz parameter */
    )
{
    return (char*)(foo - baz);
}

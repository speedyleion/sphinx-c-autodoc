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
 * Doxygen style function
 *
 * This function has no returns section, but has a `discussion` section as
 * described by clang.
 *
 * In Fact this has multiple discussion paragraphs.
 *
 * @param water An element
 * @param air A different element
 */
void doxy_documented_parameters_no_returns(int water, int air)
{
    printf("%d", water - air);
}

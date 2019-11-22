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
 * Function with documented parameters
 *
 * :param param1: The first parameter which is on multiple lines
 *      with this being the second line.
 * :param param2: An alternative second parameter
 *
 * :returns: Some return value.
 */
int documented_parameters(int param1, int param2)
{
    return param1 - param2;
}

/******************************************************************************
*
* This is a file comment. The *first* comment in the file will be grabbed.
* Often times people put the copyright in these. If that is the case then you
* may want to utilize the pre parse hook (TODO MAKE PRE-PARSE HOOK).
*
* One may notice that this comment block has a string of `***` along the top
* and the bottom. For the file comment these will get stripped out, however for
* comments on other c constructs like macros, functions, etc. clang is often
* utilized and it does not understand this pattern, so again the pre-parse hook
* may be something to use to sanitize these kind of comments.
*
******************************************************************************/

/**
 * Unused include but wanted to make sure the tool didn't blow up
 */
#include <stdio.h>

/**
 * A simple macro definition
 */
#define TOO_SIMPLE

/**
 * A function like macro
 *
 * An attempt will be made to derive the arguments of the macro.  It will
 * probably work in most instances...
 *
 * As per the `function <http://www.sphinx-doc.org/en/1.0/domains.html#directive-c:function>`_
 * directive for the c domain function like macros are documented as functions.
 * This means that one can document them with the ``:param:`` and ``:returns:``
 * fields. One could even utilize the
 * `napoleon <https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html>`_
 * extension to format something like:
 *
 * Args:
 *     _a: The time of day as derived from the current temperature.
 *     _b: The place to be.
 *
 * Returns:
 *     The predicted value of stocks based on `_a`.
 */
#define MY_COOL_MACRO(_a, _b) \
    some_func((_a))

/**
 * Structures can be documented.
 *
 * When the structure is anonymous and hidden inside a typedef, like this one,
 * it will be documented using the typedefed name.
 *
 * The members can be documented with individual comments, or they can use a
 * members section. This example struct documents the members with individual
 * comments.
 */
typedef struct
{
    float first_member; /**< The first member of this specific structure
                             using a trailing comment, notice the ``<`` after
                             the comment start */
    /**
     * This member is documented with a comment proceeding the member.
     */
    int second_member;
} a_struct_using_member_comments;

/**
 * This example structure uses the `Members:` section and lets napoleon format
 * the members.
 *
 * Members:
 *     one: The first member of parent struct
 *     two: This is a structure declared in the parent struct its children are
 *         documented below.
 *         Members:
 *             nested_one: The nested member documentation
 *             nested_two: The second nested member documentation
 *     three: The third member of parent struct
 *
 */
struct members_documented_with_napoleon
{
    int one;
    struct {
        float nested_one;
        int nested_two;
    } two;
    float three;
};

/**
 * Enumerations are considered macros. If you want to documente them with
 * napoleon then you use the section title `Enumerations:`.
 *
 * Enumerations:
 *     THE_FIRST_ENUM: Used for the first item
 *     THE_SECOND_ENUM: Second verse same as the first.
 *     THE_THIRD_ENUM: Not once, note twice, but thrice.
 *     THE_LAST_ENUM: Just to be sure.
 */
typedef enum{
    THE_FIRST_ENUM, /**< Documentation in a comment for THE_FIRST_ITEM,
                      * note this is trailing for some reason clang will
                      * apply leading comments to *all* the enumerations */
    THE_SECOND_ENUM = 30,
    THE_THIRD_ENUM = THE_SECOND_ENUM,
    THE_LAST_ENUM
} some_enum;


/**
 * File level variables can also be documented
 */
int some_flag_variable;

/**
 * Even structures defined in variables can be handled.
 */
struct {
    int a;
    float b;
} inline_struct_variable = {1, 3.0f};

/**
* This is a function comment. The parameters from this are much easier to
* derive than those from a function like macro so they should always be
* correct.
*
* Since the backend parser is clang and clang supports
* `doxygen style comments <https://llvm.org/devmtg/2012-11/Gribenko_CommentParsing.pdf>`_
* One can document functions using normal doxygen style markup.
*
* @param hello: The amount of hello appericiations seen so far.
* @param what: The common reply character seen.
*
* @returns The increase on hello's in order to maintain politeness.
*
*/
int my_func(float hello, char what)
{
    printf("hello %c", what);

    return (int)hello + 5;
}

/**
 * One can also use Goolge style docstrings with napoleon for documenting
 * functions.
 *
 * .. note:: Functions do not support mixing doxygen style and napoleon
 *     style documentation.
 *
 * Parameters:
 *     yes: A progressive rock band from the 70s.
 *     another_one: Yet one more parameter for this function.
 *
 * Returns:
 *     The square root of 4, always.
 */
int napoleon_documented_function(int yes, int another_one)
{
    return 2;
}
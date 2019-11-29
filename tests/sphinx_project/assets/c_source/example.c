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
 *     int foo: The foo like member for foo like things.
 *     bar: The bar like member
 *
 */
struct members_documented_with_napoleon
{
    int foo;
    char bar;
};

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
 * A structure containing an inline declared structure field.
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
struct nested_struct
{
    int one;
    struct {
        float nested_one;
        int nested_two;
    } two;
    float three;
};
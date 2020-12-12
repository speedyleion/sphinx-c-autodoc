/**
 * File focusing on variables
 */

// Provide a way to mix defines into an unknown variable's type
#define MAYBE_CONST

/**
 * A variable
 */
static const char * file_level_variable = "hello";

/**
 * A variable with unknown type
 * This one we can parse the tokens and try to replace clang's ``int``
 * usage with a stab at the underlying type.  We can't take this token
 * for token as sphinx is too strict at parsing and will assume that
 * ``MAYBE_CONST`` is the type.
 */
static MAYBE_CONST /* throw in a pinch of comment to the mix */
    unknown_type * unknown_type_var = 30;

/**
 * A an array variable with an unknown type.
 * For whatever reason clang will come back with no extent on this so
 * we have to fall back to this being treated as an int
*/
unknown_type unknown_array_type_var[24];

/**
 * Unknown extern type
 */
extern unknown_type * unknown_extern_type_var;

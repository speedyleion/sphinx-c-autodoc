/**
 * Defines in C files are inherently private.
 */
#define PRIVATE_MACRO 3

/**
 * Function macros in C files should also be private
 */
#define PRIVATE_FUNCTION_MACRO(_a, _b)\
    (_a) + (_b)

/**
 * Types, in c files are inherently private.
 */
typedef int foo;

/**
 * static variables are inherently private
 */
static int my_var;

/**
 * Non static variables are not private
 */
float a_public_var;

/**
 * Enumerations in c files are inherently private
 */
enum private_enum {
    ENUM_1
};

/**
 * structures in c files are inherently private
 */
struct private_struct {
    int a;
};

/**
 * Non static functions are not private
 */
void function1(int a);

/**
 * static functions, in c files are inherently private.
 */
static void function2(int a);

#define LEADING_UNDOCUMENTED_MACRO "undocumented macro which is at the begining of a file so no tokens will be grabbed"
/**
 * A typedef comment
 */
typedef int bar;

/**
 * A define of something.
 */
#define MY_D_FINE 30

#define UNDOCUMENTED_MACRO 20

/*
 * A non document comment which won't get picked up a macro comment
 */
#define NON_DOC_COMMENT "see comment description"


/**
 * A function like macro with 2 parameters
 */
#define FUNCTION_LIKE_MACRO(_x, _y) \
    foo((_x), (_y))
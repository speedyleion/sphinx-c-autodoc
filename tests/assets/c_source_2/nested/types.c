/**
 * This is basic typedef from a native type to another name.
 */
typedef int my_int;

/**
 * A struct that is actually anonymouse but is typedefed in place.
 *
 * Members:
 *     bar: The bar like member for bar like things. This is multiple lines to make
 *         sure the parsing logic is correct.
 *     baz: The baz like member
 */
typedef struct
{
int bar;
float baz;
} my_struct_type;

/**
 * A plain struct that is *not* typedefed.
 */
struct some_struct
{
    my_struct_type foo;
    int a;
};

typedef some_struct intermediate_type;

/**
 * A typedef of a struct after the fact.
 */
typedef intermediate_type typedefed_struct;


typedef char undocumented;

/**
 * A struct with documented members
 */
struct documented_members
{
    // Note the '<' to be marked as trailing documentation comments
    // See https://llvm.org/devmtg/2012-11/Gribenko_CommentParsing.pdf
    float a; /**< The string for member a */
    float b; /**< Some other string for member b */
};

/**
 * A union type that can be documented
 */
union a_union_type
{
    float alias_a;
    int alias_b;
};

/**
 * A union type that documents in multiple places, this tests a few things:
 *
 *     - Can one put the type in the napoleon documentation? It is undefined if the
 *       types don't match.
 *     - Does the merging of the documentation successfully combine into multiple
 *       paragraphs?
 *
 * Members:
 *     float alias_a: The description for `alias_a` the napoleon style
 *         documentation includes the type.
 *     alias_b: This documentation lacks the type description but it will be taken
 *         from the declaration.
 */
union a_multiply_documented_union_type
{
    float alias_a;
    int alias_b; /**< A second paragraph for `alias_b` from the member declaration */
};

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

/**
 * A typedefed union
 */
typedef union
{
unknown_type one;
another_unknown two;
} a_union_typedef;

/**
 * A function type with unknown return type. This will for the generic parsing
 * to happen instead of the clang soup
 */

typedef unknown_return_type (function_type)(const unknown_type * foo, const unknonw_two * yes);

/**
 * A function pointer type with unknown return type
 */
typedef what (*function_pointer_type)(const int * hello, const foo_type baz);

/**
 * A function pointer wrapped on multiple lines.
 */
typedef int (*wrapped_function_pointer)
    (
    const int * hello,
    const float baz
    );

#define SOME_SIZE 10;

/**
 * A char array typedef
 */
typedef char char_array[SOME_SIZE];

/**
 * A struct with an array inside
 *
 * Members:
 *     foo: An array member with an unknown type, it will show as int.
 *     bar: An array with a known type.
 */
typedef struct
{

unknown_type foo[SOME_SIZE];
float bar[SOME_SIZE];
} struct_with_array_member;

/**
 * This is basic typedef from a native type to another name.
 */
typedef int my_int;

/**
 * A struct that is actually anonymouse but is typedefed in place.
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

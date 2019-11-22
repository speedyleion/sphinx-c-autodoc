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


/**
 * A typedef of a struct after the fact.
 */
typedef some_struct typedefed_struct;

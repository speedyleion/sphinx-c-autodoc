// Test case example of the issue that was reported in
// https://github.com/speedyleion/sphinx-c-autodoc/issues/174

/**
 * My Define
 */
#define MY_BITMASK  0x8000U

/**
 * My Define mask
 */
#define MY_MASKED( base_enum ) ((base_enum) | MY_BITMASK )

/**
 * My enum
 */
typedef enum {
    VALUE_0,          /**< my value 0*/
    VALUE_1,          /**< my value 1*/
    VALUE_2 = MY_MASKED( VALUE_0 ),     /**< my value 2*/
    VALUE_3 = MY_MASKED( VALUE_1 ),     /**< my value 3*/
} my_value_e;
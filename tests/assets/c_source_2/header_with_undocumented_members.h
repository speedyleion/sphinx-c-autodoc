/**
 * This header file as some undocumented contents
 */
#ifndef _MY_HEADER_GUARD
#define _MY_HEADER_GUARD

typedef struct {
int foo;
float what;
} undocumented_struct;

/**
 * The structure member `bar` is undocumented.  It will still show in the
 * documentation, only file level constructs will be filtered with this
 * option.
 */
typedef struct {
int bar;
} struct_with_undocumented_member;

#endif /* _MY_HEADER_GUARD */

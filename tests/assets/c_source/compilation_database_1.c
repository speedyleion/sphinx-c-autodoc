/*
A file which has 2 different define paths based on SOME_DEFINE
*/

/*
This include won't be found because the compile commands for this file does
*not* have the include path.  This means that the functions will return *int*s
instead of the normal :type:`some_type`.
*/
#include "some_include.h"

#ifdef SOME_DEFINE
/**
This is a version of `foo` which is only available when the define
SOME_DEFINE is available.
*/
some_type foo(int a){
return (some_type)(a + 3);
}
#else
/**
This is a version of `foo` that is normally available from this module
*/
some_type foo(int a, int b){
return (some_type)(a + b);
}
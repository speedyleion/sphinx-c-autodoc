/*
A file which shows how an include made available via a compilation database
can fully resolve a function.
*/

/*
This include will only be found if the compilation database is used and has an
include option available.
*/
#include "some_include.h"

#ifdef INCLUDE_FOUND
/**
When the include is found this will return a float instead of some_type.
*/
float foo(int a){
return (float)(a + 3);
}
#else
/**
When the include is not found this will return some_type.
*/
some_type foo(int a){
return (some_type)(a + 3);
}
#endif
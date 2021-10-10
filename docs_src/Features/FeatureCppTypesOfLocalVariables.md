# C++ types of local variables
YYC Boost can inject native C++ types into local variables. These types should
be compatible with GML:

```cpp
const char*
int
double
```

Write a comment `/*:cpp_type*/` after variable name to specify its C++ type.

```gml
#macro COUNT 10000
var _t;

_t = get_timer();
for (var i = 0; i < COUNT; ++i) {}
show_debug_message(get_timer() - _t);

// This loop runs faster compared to when a regular var is used
_t = get_timer();
for (var j/*:int*/= 0; j < COUNT; ++j) {}
show_debug_message(get_timer() - _t);
```

## Known limitations
Variable types can be defined only once for `var`s with the same name in the
same scope! In the following code the variable `_a` would always be defined as
an `int`.

```gml
if (wholeNumbersOnly)
{
    var _a/*:int*/ = 0;
}
else
{
    var _a/*:double*/ = 0.0;
}
```

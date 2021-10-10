# C++ code injection
You can entirely replace all contents of a function with a custom C++ code by
writing comments `/*cpp C++ code here... */`:

```gml
/// @desc Returns 1 when YYC Boost is used, otherwise 0.
function is_cpp()
{
    /*cpp
    _result = 1;
    return _result;
    */
    return 0;
}
```

Anonymous functions work too:

```gml
function mul(_a)
{
    return (function (_a) {
        /*cpp
        _result = (*_args[0]) * 2.0;
        return _result;
        */
        return _a;
    })(_a);
}

mul(10); // Prints 10 in VM and 20 in YYC
```

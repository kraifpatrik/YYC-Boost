# YYC Boost
> Inject custom C++ code into GameMaker Studio 2 YYC builds!

[![License](https://img.shields.io/github/license/kraifpatrik/YYCBoost)](LICENSE)

# Table of Contents
* [Features](#features)
* [Documentation](#documentation)
* [Building from source code](#building-from-source-code)
* [Support the project](#support-the-project)
* [Links](#links)

# Features
## Multithreading
Run functions in a separate thread!

```gml
yyc_run_in_thread(function () {
    while (true)
    {
        show_debug_message("This does not block the main thread!");
    }
});
```

## Task system
Utilize multithreading for parallel tasks! Includes fallback for VM.

```gml
var _sleepTask = function (_arg) {
    var _ms = _arg[0];
    var _message = _arg[1];
    var _t = current_time;
    while (current_time - _t < _ms) {}
    show_debug_message(_message);
};

// Create standalone tasks:
new YYC_Task(_sleepTask, [1000, "Standalone task done!"]).Run();

// Or groups of tasks:
new YYC_GroupTask([
    new YYC_Task(_sleepTask, [1000, "Task 1 done!"]),
    new YYC_Task(_sleepTask, [2000, "Task 2 done!"]),
    new YYC_Task(_sleepTask, [3000, "Task 3 done!"]),
], _sleepTask, [1000, "Group 1 done!"]).Run();
```

## C++ types of local variables
Define C++ type of a `var` to save memory and increase performance!

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

## C++ code injection
Replace function with a custom C++ code!

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

# Documentation
Online documentation for the latest release of YYC Boost is available [here](https://kraifpatrik.com/docs/yycboost).

# Building from source code
**Requires [Python 3](https://www.python.org/)!**

```cmd
git clone https://github.com/kraifpatrik/YYCBoost
cd .\YYCBoost\YYCBoost_CLI\
python.exe -m venv env
.\env\Scripts\activate
pip.exe install -r requirements.txt
python.exe setup.py
```

This will create a directory `YYCBoost\YYCBoost_CLI\dist` with `yycboost.exe`.

# Support the project
If you like YYC Boost and you would like to support its further development, you can donate to [paypal.me/kraifpatrik](https://paypal.me/kraifpatrik/10usd).

# Links
* [Documentation](https://kraifpatrik.com/docs/yycboost)
* [Donate](https://paypal.me/kraifpatrik/10usd)
* [Website](https://kraifpatrik.com)

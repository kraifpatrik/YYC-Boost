global.__timeoutList = ds_list_create();
global.__timeoutMutex = new YYC_Mutex();

/// @func Timeout(_name, _duration, _func[, _arg])
/// @desc Enqueues a function to be executed after certain number of milliseconds.
/// @param {string} _name The name of the timeout.
/// @param {real} _duration The duration of the timeout in milliseconds.
/// @param {func} _func A function to execute after the timeout. It will be passed
/// `_arg` as the first argument and the timeout instance as the second.
/// @param {any} [_arg] An optional argument for `_func`. Defaults to `undefined`.
/// @example
/// ```gml
/// var _t = new Timeout("Sleep", 1000, function () {
///     show_debug_message("Timer " + Name + " slept for " + string(Duration) + "ms!");
/// });
/// ```
/// @see process_timeouts
function Timeout(_name, _duration, _func, _arg=undefined) constructor
{
	/// @var {string} The name of the timeout.
	/// @readonly
	Name = _name;

	/// @var {real} The duration of the timeout in milliseconds.
	/// @readonly
	Duration = _duration;

	/// @var {func} A function to execute after the timeout ends.
	/// @readonly
	Func = _func;

	/// @var {any} An optional argument for the timeout function.
	/// @readonly
	Arg = _arg;

	Start = current_time;

	global.__timeoutMutex.Acquire();
	ds_list_add(global.__timeoutList, self);
	global.__timeoutMutex.Release();
}

/// @func process_timeouts()
/// @desc Processes timeouts. Call this every step if YYC Boost is not available.
/// @example
/// ```gml
/// if (!yyc_is_boost())
/// {
///    process_timeouts();
/// }
/// ```
/// @see Timeout
function process_timeouts()
{
	global.__timeoutMutex.Acquire();
	for (var i/*:int*/ = ds_list_size(global.__timeoutList) - 1; i >= 0; --i)
	{
		var _timeout = global.__timeoutList[| i];
		if (current_time - _timeout.Duration >= _timeout.Start)
		{
			_timeout.Func(_timeout.Arg, _timeout);
			ds_list_delete(global.__timeoutList, i);
		}
	}
	global.__timeoutMutex.Release();
}

if (yyc_is_boost())
{
	yyc_run_in_thread(function () {
		while (true)
		{
			process_timeouts();
		}
	});
}
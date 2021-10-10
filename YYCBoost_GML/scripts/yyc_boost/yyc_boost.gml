/// @func yyc_is_boost()
/// @desc Checks whether YYC Boost is activated.
/// @return {bool} Returns true if YYC Boost is activated.
function yyc_is_boost()
{
	/*cpp
	_result = 1;
	return _result;
	*/
	return false;
}

/// @func yyc_get_cpu_count()
/// @desc Retrieves number of logical CPUs.
/// @return {uint} The number of logical CPUs. This will always be 1 when
/// YYC Boost is not activated.
function yyc_get_cpu_count()
{
	/*cpp
	_result = SCPU::GetCPUCount();
	return _result;
	*/
	return 1;
}

/// @func yyc_run_in_thread(_func[, _arg])
/// @desc Runs a function in a separate thread.
/// @param {func} _func The function to run.
/// @param {any} [_arg] An argument for the function. Defaults to `undefined`.
/// @throws {YYC_Exception} If threads are not available.
/// @example
/// ```gml
/// yyc_run_in_thread(function (_timeout) {
///     var _t = current_time;
///     while (current_time - _t < _timeout) {}
///     show_debug_message("Slept for " + string(_timeout) + "ms!");
/// }, 1000);
/// ```
function yyc_run_in_thread(_func, _arg=undefined)
{
	/*cpp RUN_IN_THREAD_BODY; */
	throw new YYC_Exception("Threads are not available!");
}
/// @func YYC_Task(_func[, _arg])
///
/// @desc A task.
///
/// @param {func} _func A function executed by the task. It will be passed `_arg`
/// as the first argument and the task instance as the second.
/// @param {any} [_arg] An optional argument for the task function. Defaults to
/// `undefined`.
///
/// @example
/// Creates a task that sleeps for 1 second and then prints a message.
///
/// ```gml
/// // Create event
/// new YYC_Task(function (_ms) {
///     var _t = current_time;
///     while (current_time - _t < _ms) {}
///     show_debug_message("Slept for " + string(_ms) + "ms!");
/// }, 1000).Run();
/// 
/// // Step event
/// if (!yyc_is_boost())
/// {
///     yyc_tasks_update();
/// }
/// ```
///
/// @see YYC_GroupTask
/// @see yyc_tasks_update
function YYC_Task(_func, _arg=undefined) constructor
{
	/// @var {func} A function executed by the task.
	/// @readonly
	Func = _func;

	/// @var {any} An argument for the task function.
	/// @readonly
	Arg = _arg;

	/// @var {YYC_GroupTask/undefined} The parent of the task.
	/// @readonly
	Parent = undefined;

	/// @func Run()
	/// @desc Enqueues the task for execution.
	/// @return {YYC_Task} Returns `self`.
	/// @see yyc_tasks_update
	static Run = function () {
		gml_pragma("forceinline");
		Enqueue();
		return self;
	};

	/// @private
	static Enqueue = function () {
		gml_pragma("forceinline");
		global.__yycTaskMutex.Acquire();
		ds_queue_enqueue(global.__yycTasks, self);
		global.__yycTaskMutex.Release();
		global.__yycTaskSemaphore.Release();
	};

	/// @private
	static Execute = function () {
		gml_pragma("forceinline");
		Func(Arg, self);
		if (Parent != undefined)
		{
			global.__yycTaskMutex.Acquire();
			var _groupFinished = (--Parent.Counter == 0);
			global.__yycTaskMutex.Release();
			if (_groupFinished)
			{
				Parent.Enqueue();
			}
		}
	};
}
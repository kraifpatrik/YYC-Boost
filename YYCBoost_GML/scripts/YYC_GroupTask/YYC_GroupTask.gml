/// @func YYC_GroupTask(_children, _func[, _arg])
///
/// @extends YYC_Task
///
/// @desc A group of tasks executed in parallel. The group task's function is
/// executed when they are all finished.
///
/// @param {YYC_Task[]} _children An array of tasks executed within the group.
/// @param {func} _func A function executed when all child tasks are finished.
/// It will be passed `_arg` as the first argument and the task instance as the
/// second.
/// @param {any} [_arg] An optional argument for the task function. Defaults to
/// `undefined`.
///
/// @example
/// Following example creates a group of tasks which sleep for 1,2 and 3 seconds
/// and then show a message. When they are all finished, the group task itself
/// sleeps for another 1 second and then shows a message. Without YYC Boost this
/// would take 7 seconds in total, as the tasks cannot be executed in parallel.
/// With YYC Boost and at least 3 threads (one for each job within the group)
/// this takes 4 seconds.
///
/// ```gml
/// // Create event
/// var _sleepTask = function (_arg) {
///     var _ms = _arg[0];
///     var _message = _arg[1];
///     var _t = current_time;
///     while (current_time - _t < _ms) {}
///     show_debug_message(_message);
/// };
///
/// new YYC_GroupTask([
///     new YYC_Task(_sleepTask, [1000, "Task 1 done!"]),
///     new YYC_Task(_sleepTask, [2000, "Task 2 done!"]),
///     new YYC_Task(_sleepTask, [3000, "Task 3 done!"]),
/// ], _sleepTask, [1000, "Group 1 done!"]).Run();
///
/// // Step event
/// if (!yyc_is_boost())
/// {
///     yyc_tasks_update();
/// }
/// ```
///
/// @see YYC_Task
function YYC_GroupTask(_children, _func, _arg=undefined)
	: YYC_Task(_func, _arg) constructor
{
	/// @var {YYC_Task[]} An array of child tasks.
	/// @readonly
	Children = _children;

	/// @var {uint} Number of child tasks awaiting for execution.
	/// @private
	Counter = array_length(_children);

	for (var i = Counter - 1; i >= 0; --i)
	{
		Children[i].Parent = self;
	}

	static Run = function () {
		gml_pragma("forceinline");
		var _counter = Counter;
		for (var i = 0; i < _counter; ++i)
		{
			Children[i].Run();
		}
		return self;
	};
}
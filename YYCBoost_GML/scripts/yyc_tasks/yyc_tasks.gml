/// @macro {real} Number of milliseconds available for executing tasks in
/// a single frame when multithreading is not available (e.g. in VM).
#macro YYC_TASKS_MS_PER_FRAME 8

/// @macro {real} Number of threads for task processing. Minimum is 1.
/// Defaults to number of logical CPUs - 1.
#macro YYC_TASKS_THREAD_COUNT max(yyc_get_cpu_count() - 1, 1)

global.__yycTaskMutex = new YYC_Mutex();
global.__yycTasks = new YYC_Queue();

if (yyc_is_boost())
{
	repeat (YYC_TASKS_THREAD_COUNT)
	{
		yyc_run_in_thread(function () {
			while (true)
			{
				var _task = global.__yycTasks.Dequeue();
				if (_task)
				{
					_task.Execute();
				}
				var _t = current_time;
				while (current_time - _t < 100) {}
			}
		});
	}
}

/// @func yyc_tasks_update()
/// @desc Executes tasks in a single thread. This should be called every frame
/// in the step event of a controller object if YYC Boost is not available. You
/// can control how much time in a single frame can be used for executing tasks
/// through [YYC_TASKS_MS_PER_FRAME](./YYC_TASKS_MS_PER_FRAME.html), but at least
/// one task is always executed if available.
/// @example
/// ```gml
/// if (!yyc_is_boost())
/// {
///     yyc_tasks_update();
/// }
/// ```
/// @see yyc_is_boost
/// @see YYC_TASKS_MS_PER_FRAME
function yyc_tasks_update()
{
	var _t = get_timer();
	while (!global.__yycTasks.Empty())
	{
		global.__yycTasks.Dequeue().Execute();
		if ((get_timer() - _t) * 0.001 >= YYC_TASKS_MS_PER_FRAME)
		{
			break;
		}
	}
}
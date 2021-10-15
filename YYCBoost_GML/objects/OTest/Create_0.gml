show_debug_message("CPU count: " + string(yyc_get_cpu_count()));

mutex = new YYC_Mutex();
arr = [];

function test(_args)
{
	var _self = _args[0];
	var _value = _args[1];

	show_debug_message("begin:" + string(_value));

	var _t = current_time;
	while (current_time - _t < 500) {}

	_self.mutex.Acquire();
	array_push(_self.arr, _value);
	_self.mutex.Release();

	show_debug_message("finish:" + string(_value));
}
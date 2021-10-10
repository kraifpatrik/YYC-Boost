show_debug_message("CPU count: " + string(yyc_get_cpu_count()));

var _t = new Timeout("Sleep", 5000, function () {
	show_debug_message("Slept for 5s!");
});
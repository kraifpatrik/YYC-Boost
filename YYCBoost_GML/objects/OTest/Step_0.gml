if (!yyc_is_boost())
{
	yyc_tasks_update();
	process_timeouts();
}

if (keyboard_check_pressed(vk_enter))
{
	for (var i/*:int*/ = 0; i < 10; ++i)
	{
		new YYC_Task(test, [self, i]).Run();
	}
}
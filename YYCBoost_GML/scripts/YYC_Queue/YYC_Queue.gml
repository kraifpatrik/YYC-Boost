function YYC_Queue() constructor
{
	Queue = ds_queue_create();

	Mutex = new YYC_Mutex();

	/// @return {bool}
	static Empty = function () {
		gml_pragma("forceinline");
		Mutex.Acquire();
		var _empty = ds_queue_empty(Queue);
		Mutex.Release();
		return _empty;
	};

	static Enqueue = function (_value) {
		gml_pragma("forceinline");
		Mutex.Acquire();
		ds_queue_enqueue(Queue, _value);
		Mutex.Release();
		return self;
	};

	static Dequeue = function () {
		gml_pragma("forceinline");
		var _retval = undefined;
		Mutex.Acquire();
		if (!ds_queue_empty(Queue))
		{
			_retval = ds_queue_dequeue(Queue);
		}
		Mutex.Release();
		return _retval;
	};

	static Destroy = function () {
		gml_pragma("forceinline");
		ds_queue_destroy(Queue);
		Mutex.Destroy();
	};
}
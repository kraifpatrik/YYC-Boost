/// @func yyc_mutex_create()
/// @desc Creates a new mutex.
/// @return {int} The id of the mutex.
/// @see yyc_mutex_acquire
/// @see yyc_mutex_release
function yyc_mutex_create()
{
	/*cpp
	_result = (new CMutex())->GetId();
	return _result;
	*/
}

/// @func yyc_mutex_acquire(_id)
/// @desc Blocks until a mutex is acquired.
/// @param {int} _id The id of the mutex.
/// @see yyc_mutex_create
/// @see yyc_mutex_release
function yyc_mutex_acquire(_id)
{
	/*cpp
	int id = (int)ARGUMENT(0).asReal();
	CMutex* mutex = ObjectFromId<CMutex>(id);
	mutex->Acquire();
	*/
}

/// @func yyc_mutex_release(_id)
/// @desc Releases an acquired mutex.
/// @param {int} _id The id of the mutex.
/// @return {bool} Returns `true` if the mutex was released.
/// @see yyc_mutex_create
/// @see yyc_mutex_acquire
function yyc_mutex_release(_id)
{
	/*cpp
	int id = (int)ARGUMENT(0).asReal();
	CMutex* mutex = ObjectFromId<CMutex>(id);
	_result = mutex->Release() ? 1 : 0;
	return _result;
	*/
}

/// @func yyc_mutex_destroy(_id)
/// @desc Destroys a mutex.
/// @param {int} _id The id of the mutex.
function yyc_mutex_destroy(_id)
{
	/*cpp
	int id = (int)ARGUMENT(0).asReal();
	CMutex* mutex = ObjectFromId<CMutex>(id);
	delete mutex;
	*/
}

/// @func YYC_Mutex()
///
/// @desc An OOP wrapper for mutex functions.
///
/// @see yyc_mutex_create
/// @see yyc_mutex_acquire
/// @see yyc_mutex_release
/// @see yyc_mutex_destroy
function YYC_Mutex() constructor
{
	/// @var {int} The id of the mutex.
	/// @readonly
	Id = yyc_mutex_create();

	/// @func Acquire()
	/// @desc Blocks until the mutex is acquired.
	/// @return {YYC_Mutex} Returns `self`.
	/// @see YYC_Mutex.Release
	static Acquire = function () {
		gml_pragma("forceinline");
		yyc_mutex_acquire(Id);
		return self;
	};

	/// @func Release()
	/// @desc Releases the acquired mutex.
	/// @return {bool} Returns `true` if the mutex was released.
	/// @see YYC_Mutex.Acquire
	static Release = function () {
		gml_pragma("forceinline");
		return yyc_mutex_release(Id);
	};

	/// @func Destroy()
	/// @desc Destroys the mutex.
	static Destroy = function () {
		gml_pragma("forceinline");
		yyc_mutex_destroy(Id);
	};
}
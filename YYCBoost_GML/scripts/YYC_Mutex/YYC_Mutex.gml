/// @func yyc_mutex_create(_name)
/// @desc Creates a new mutex.
/// @param {string} _name The name of the mutex.
/// @see yyc_mutex_acquire
/// @see yyc_mutex_release
function yyc_mutex_create(_name)
{
	/*cpp SMutex::Create(*_args[0]); */
}

/// @func yyc_mutex_acquire(_name)
/// @desc Blocks until a mutex is acquired.
/// @param {string} _name The name of the mutex.
/// @see yyc_mutex_create
/// @see yyc_mutex_release
function yyc_mutex_acquire(_name)
{
	/*cpp SMutex::Acquire(*_args[0]); */
}

/// @func yyc_mutex_release(_name)
/// @desc Releases an acquired mutex.
/// @param {string} _name The name of the mutex.
/// @see yyc_mutex_create
/// @see yyc_mutex_acquire
function yyc_mutex_release(_name)
{
	/*cpp SMutex::Release(*_args[0]); */
}

/// @func yyc_mutex_destroy(_name)
/// @desc Destroys a mutex.
/// @param {string} _name The name of the mutex.
function yyc_mutex_destroy(_name)
{
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
	static IdNext = 0;

	/// @var {string} The name of the mutex.
	/// @readonly
	Name = "Mutex" + string(IdNext++);

	/// @func Acquire()
	/// @desc Blocks until the mutex is acquired.
	/// @return {YYC_Mutex} Returns `self`.
	/// @see YYC_Mutex.Release
	static Acquire = function () {
		gml_pragma("forceinline");
		yyc_mutex_acquire(Name);
		return self;
	};

	/// @func Release()
	/// @desc Releases the acquired mutex.
	/// @return {YYC_Mutex} Returns `self`.
	/// @see YYC_Mutex.Acquire
	static Release = function () {
		gml_pragma("forceinline");
		yyc_mutex_release(Name);
		return self;
	};

	/// @func Destroy()
	/// @desc Destroys the mutex.
	static Destroy = function () {
		gml_pragma("forceinline");
		yyc_mutex_destroy(Name);
	};

	yyc_mutex_create(Name);
}
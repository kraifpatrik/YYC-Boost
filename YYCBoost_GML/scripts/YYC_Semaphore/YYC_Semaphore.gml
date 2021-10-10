/// @func yyc_semaphore_create(_name, _initial, _max)
/// @desc Creates a new semaphore.
/// @param {string} _name The name of the semaphore.
/// @param {int} _initial Initial value of the semaphore.
/// @param {uint} _max Maximum value of the semaphore.
/// @see yyc_semaphore_acquire
/// @see yyc_semaphore_release
function yyc_semaphore_create(_name, _initial, _max)
{
	/*cpp
	SSemaphore::Create(
		*_args[0],
		(int)(*_args[1]).asReal(),
		(int)(*_args[2]).asReal());
	*/
}

/// @func yyc_semaphore_acquire(_name)
/// @desc Blocks until a semaphore is acquired.
/// @param {string} _name The name of the semaphore.
/// @see yyc_semaphore_create
/// @see yyc_semaphore_release
function yyc_semaphore_acquire(_name)
{
	/*cpp SSemaphore::Acquire(*_args[0]); */
}

/// @func yyc_semaphore_release(_name)
/// @desc Releases an acquired semaphore.
/// @param {string} _name The name of the semaphore.
/// @see yyc_semaphore_create
/// @see yyc_semaphore_acquire
function yyc_semaphore_release(_name)
{
	/*cpp SSemaphore::Release(*_args[0]); */
}

/// @func yyc_semaphore_destroy(_name)
/// @desc Destroys a semaphore.
/// @param {string} _name The name of the semaphore.
function yyc_semaphore_destroy(_name)
{
}

/// @func YYC_Semaphore(_initial, _max)
///
/// @desc An OOP wrapper for semaphore functions.
///
/// @param {int} _initial Initial value of the semaphore.
/// @param {uint} _max Maximum value of the semaphore.
///
/// @see yyc_semaphore_create
/// @see yyc_semaphore_acquire
/// @see yyc_semaphore_release
/// @see yyc_semaphore_destroy
function YYC_Semaphore(_initial, _max) constructor
{
	static IdNext = 0;

	/// @var {string} The name of the semaphore.
	/// @readonly
	Name = "Semaphore" + string(IdNext++);

	/// @var {int} The initial value of the semaphore.
	/// @readonly
	Initial = _initial;

	/// @var {uint} The maximum value of the semaphore.
	/// @readonly
	Max = _max;

	/// @func Acquire()
	/// @desc Blocks until the semaphore is acquired.
	/// @return {YYC_Semaphore} Returns `self`.
	static Acquire = function () {
		gml_pragma("forceinline");
		yyc_semaphore_acquire(Name);
		return self;
	};

	/// @func Release()
	/// @desc Releases the acquired semaphore.
	/// @return {YYC_Semaphore} Returns `self`.
	static Release = function () {
		gml_pragma("forceinline");
		yyc_semaphore_release(Name);
		return self;
	};

	/// @func Destroy()
	/// @desc Destroys the semaphore.
	static Destroy = function () {
		gml_pragma("forceinline");
		yyc_semaphore_destroy(Name);
	};

	yyc_semaphore_create(Name, Initial, Max);
}
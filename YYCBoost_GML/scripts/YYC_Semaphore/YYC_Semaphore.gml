/// @func yyc_semaphore_create(_initial, _max)
/// @desc Creates a new semaphore.
/// @param {uint} _initial Initial value of the semaphore.
/// @param {uint} _max Maximum value of the semaphore.
/// @return {int} Returns the id of the semaphore.
/// @see yyc_semaphore_acquire
/// @see yyc_semaphore_release
function yyc_semaphore_create(_initial, _max)
{
	/*cpp
	int initial = (int)ARGUMENT(0).asReal();
	int max = (int)ARGUMENT(1).asReal();
	_result = (new CSemaphore(initial, max))->GetId();
	return _result;
	*/
}

/// @func yyc_semaphore_acquire(_id)
/// @desc Blocks until a semaphore is acquired.
/// @param {int} _id The id of the semaphore.
/// @see yyc_semaphore_create
/// @see yyc_semaphore_release
function yyc_semaphore_acquire(_id)
{
	/*cpp
	int id = (int)ARGUMENT(0).asReal();
	CSemaphore* semaphore = ObjectFromId<CSemaphore>(id);
	semaphore->Acquire();
	*/
}

/// @func yyc_semaphore_release(_id)
/// @desc Releases an acquired semaphore.
/// @param {int} _id The name of the semaphore.
/// @return {bool} Returns `true` if the semaphore was released.
/// @see yyc_semaphore_create
/// @see yyc_semaphore_acquire
function yyc_semaphore_release(_id)
{
	/*cpp
	int id = (int)ARGUMENT(0).asReal();
	CSemaphore* semaphore = ObjectFromId<CSemaphore>(id);
	_result = semaphore->Release() ? 1 : 0;
	return _result;
	*/
}

/// @func yyc_semaphore_destroy(_id)
/// @desc Destroys a semaphore.
/// @param {int} _id The name of the semaphore.
function yyc_semaphore_destroy(_id)
{
	/*cpp
	int id = (int)ARGUMENT(0).asReal();
	CSemaphore* semaphore = ObjectFromId<CSemaphore>(id);
	delete semaphore;
	*/
}

/// @func YYC_Semaphore(_initial, _max)
///
/// @desc An OOP wrapper for semaphore functions.
///
/// @param {uint} _initial Initial value of the semaphore.
/// @param {uint} _max Maximum value of the semaphore.
///
/// @see yyc_semaphore_create
/// @see yyc_semaphore_acquire
/// @see yyc_semaphore_release
/// @see yyc_semaphore_destroy
function YYC_Semaphore(_initial, _max) constructor
{
	/// @var {int} The id of the semaphore.
	/// @readonly
	Id = yyc_semaphore_create(_initial, _max);

	/// @var {uint} The initial value of the semaphore.
	/// @readonly
	Initial = _initial;

	/// @var {uint} The maximum value of the semaphore.
	/// @readonly
	Max = _max;

	/// @func Acquire()
	/// @desc Blocks until the semaphore is acquired.
	/// @return {YYC_Semaphore} Returns `self`.
	/// @see YYC_Semaphore.Release
	static Acquire = function () {
		gml_pragma("forceinline");
		yyc_semaphore_acquire(Id);
		return self;
	};

	/// @func Release()
	/// @desc Releases the acquired semaphore.
	/// @return {bool} Returns `true` if the semaphore was released.
	/// @see YYC_Semaphore.Acquire
	static Release = function () {
		gml_pragma("forceinline");
		return yyc_semaphore_release(Id);
	};

	/// @func Destroy()
	/// @desc Destroys the semaphore.
	static Destroy = function () {
		gml_pragma("forceinline");
		yyc_semaphore_destroy(Id);
	};
}
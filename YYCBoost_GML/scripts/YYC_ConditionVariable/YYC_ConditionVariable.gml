function yyc_condition_variable_create()
{
	/*cpp
	_result = (new CConditionVariable())->GetId();
	return _result;
	*/
}

/// @func yyc_condition_variable_wait(_id, _criticalSection)
/// @param {int} _id
/// @param {int} _criticalSection
function yyc_condition_variable_wait(_id, _criticalSection)
{
	/*cpp
	int id = (int)ARGUMENT(0).asReal();
	int criticalSectionId = (int)ARGUMENT(1).asReal();

	CConditionVariable* conditionVariable = ObjectFromId<CConditionVariable>(id);
	CCriticalSection* criticalSection = ObjectFromId<CCriticalSection>(id);

	conditionVariable->Wait(criticalSection);
	*/
}

function yyc_condition_variable_notify_one(_id)
{
	/*cpp
	int id = (int)ARGUMENT(0).asReal();
	CConditionVariable* conditionVariable = ObjectFromId<CConditionVariable>(id);
	conditionVariable->NotifyOne();
	*/
}

function yyc_condition_variable_notify_all(_id)
{
	/*cpp
	int id = (int)ARGUMENT(0).asReal();
	CConditionVariable* conditionVariable = ObjectFromId<CConditionVariable>(id);
	conditionVariable->NotifyAll();
	*/
}

function yyc_condition_variable_destroy(_id)
{
	/*cpp
	int id = (int)ARGUMENT(0).asReal();
	CConditionVariable* conditionVariable = ObjectFromId<CConditionVariable>(id);
	delete conditionVariable;
	*/
}

/// @func YYC_ConditionVariable()
function YYC_ConditionVariable() constructor
{
	/// @var {int} The id of the condition variable.
	/// @readonly
	Id = yyc_condition_variable_create();

	/// @func Wait(_criticalSection)
	/// @param {YYC_CriticalSection}
	/// @return {YYC_ConditionVariable}
	static Wait = function (_criticalSection) {
		gml_pragma("forceinline");
		yyc_condition_variable_wait(Id, _criticalSection.Id);
		return self;
	};

	/// @func NotifyOne()
	/// @return {YYC_ConditionVariable}
	static NotifyOne = function () {
		gml_pragma("forceinline");
		yyc_condition_variable_notify_one(Id);
		return self;
	};

	/// @func NotifyAll()
	/// @return {YYC_ConditionVariable}
	static NotifyAll = function () {
		gml_pragma("forceinline");
		yyc_condition_variable_notify_all(Id);
		return self;
	};

	/// @func Destroy()
	/// @desc Destroys the condition variable.
	static Destroy = function () {
		gml_pragma("forceinline");
		yyc_condition_variable_destroy(Id);
	};
}
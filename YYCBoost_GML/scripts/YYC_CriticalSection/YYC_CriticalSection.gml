function yyc_critical_section_create()
{
	/*cpp
	_result = (new CCriticalSection())->GetId();
	return _result;
	*/
}

function yyc_critical_section_enter(_id)
{
	/*cpp
	int id = (int)ARGUMENT(0).asReal();
	CCriticalSection* criticalSection = ObjectFromId<CCriticalSection>(id);
	criticalSection->Enter();
	*/
}

function yyc_critical_section_leave(_id)
{
	/*cpp
	int id = (int)ARGUMENT(0).asReal();
	CCriticalSection* criticalSection = ObjectFromId<CCriticalSection>(id);
	criticalSection->Leave();
	*/
}


function yyc_critical_section_destroy(_id)
{
	/*cpp
	int id = (int)ARGUMENT(0).asReal();
	CCriticalSection* criticalSection = ObjectFromId<CCriticalSection>(id);
	delete criticalSection;
	*/
}

function YYC_CriticalSection() constructor
{
	Id = yyc_critical_section_create();

	static Enter = function () {
		gml_pragma("forceinline");
		yyc_critical_section_enter(Id);
		return self;
	};

	static Leave = function () {
		gml_pragma("forceinline");
		yyc_critical_section_leave(Id);
		return self;
	};

	static Destroy = function () {
		gml_pragma("forceinline");
		yyc_critical_section_destroy(Id);
	};
}
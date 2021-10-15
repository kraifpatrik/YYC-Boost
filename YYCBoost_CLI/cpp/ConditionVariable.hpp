#ifndef __CONDITION_VARIABLE_HPP__
#define __CONDITION_VARIABLE_HPP__

#include "Object.hpp"
#include "CriticalSection.hpp"
#include <windows.h>

class CConditionVariable : public CObject
{
public:
	CConditionVariable() : CObject()
	{
		InitializeConditionVariable(&ConditionVariable);
	}

	void Wait(CCriticalSection* criticalSection)
	{
		SleepConditionVariableCS(&ConditionVariable,
			criticalSection->GetRaw(), INFINITE);
	}

	void NotifyOne()
	{
		WakeConditionVariable(&ConditionVariable);
	}

	void NotifyAll()
	{
		WakeAllConditionVariable(&ConditionVariable);
	}

private:
	CONDITION_VARIABLE ConditionVariable;
};

#endif // __CONDITION_VARIABLE_HPP__

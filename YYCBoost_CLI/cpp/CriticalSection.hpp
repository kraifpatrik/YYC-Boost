#ifndef __CRITICAL_SECTION_HPP__
#define __CRITICAL_SECTION_HPP__

#include "Object.hpp"
#include <windows.h>

class CCriticalSection : public CObject
{
public:
	CCriticalSection() : CObject()
	{
		InitializeCriticalSection(&CriticalSection);
	}

	~CCriticalSection()
	{
		DeleteCriticalSection(&CriticalSection);
	}

	CRITICAL_SECTION* GetRaw()
	{
		return &CriticalSection;
	}

	void Enter()
	{
		EnterCriticalSection(&CriticalSection);
	}

	void Leave()
	{
		LeaveCriticalSection(&CriticalSection);
	}

private:
	CRITICAL_SECTION CriticalSection;
};

#endif // __CRITICAL_SECTION_HPP__

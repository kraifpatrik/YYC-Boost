#ifndef __MUTEX_HPP__
#define __MUTEX_HPP__

#include "Object.hpp"
#include <windows.h>

class CMutex : public CObject
{
public:
	CMutex() : CObject()
	{
		Mutex = CreateMutex(NULL, FALSE, NULL);
	}

	~CMutex()
	{
		CloseHandle(Mutex);
	}

	void Acquire() const
	{
		WaitForSingleObject(Mutex, INFINITE);
	}

	bool Release() const
	{
		return (ReleaseMutex(Mutex) != 0);
	}

private:
	HANDLE Mutex;
};

#endif // __MUTEX_HPP__

#ifndef __SEMAPHORE_HPP__
#define __SEMAPHORE_HPP__

#include "Object.hpp"
#include <windows.h>

class CSemaphore : public CObject
{
public:
	CSemaphore(int initial, int max) : CObject()
	{
		Semaphore = CreateSemaphore(NULL, initial, max, NULL);
	}

	~CSemaphore()
	{
		CloseHandle(Semaphore);
	}

	void Acquire() const
	{
		WaitForSingleObject(Semaphore, INFINITE);
	}

	bool Release() const
	{
		return (ReleaseSemaphore(Semaphore, 1, NULL) != 0);
	}

private:
	HANDLE Semaphore;
};

#endif // __SEMAPHORE_HPP__

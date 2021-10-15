#ifndef __THREADING_HPP__
#define __THREADING_HPP__

#include <YYGML.h>
#include <windows.h>

/** Used to pass arguments from script functions into thread functions. */
struct SThreadArgs
{
	/** This is `self` in GML. */
	CInstance* Self;

	/** This is `other` in GML. */
	CInstance* Other;

	/** Number of arguments passed to script. */
	int Count;

	/** Array of arguments passed to script. */
	YYRValue** Args;

	SThreadArgs(CInstance* pSelf, CInstance* pOther)
		: Self(pSelf)
		, Other(pOther)
		, Count(0)
		, Args(nullptr)
	{
	}

	SThreadArgs(CInstance* pSelf, CInstance* pOther, int _count,  YYRValue** _args)
		: Self(pSelf)
		, Other(pOther)
		, Count(_count)
	{
		// Copy array of arguments
		YYRValue** args = new YYRValue*[_count];
		for (int i = 0; i < _count; ++i)
		{
			args[i] = new YYRValue(*_args[i]);
		}
		this->Args = args;
	}

	~SThreadArgs()
	{
		// Delete copied arguments
		for (int i = 0; i < Count; ++i)
		{
			delete Args[i];
		}
		delete[] Args;
	}
};

struct SCPU
{
	static int GetCPUCount()
	{
		SYSTEM_INFO systemInfo;
		GetSystemInfo(&systemInfo);
		return (int) systemInfo.dwNumberOfProcessors;
	}

	static DWORD WINAPI ThreadFunc(LPVOID lpParam)
	{
		SThreadArgs* threadArgs = (SThreadArgs*)lpParam;
		CInstance* pSelf = threadArgs->Self;
		CInstance* pOther = threadArgs->Other;
		int _count = threadArgs->Count;
		YYRValue** _args = threadArgs->Args;

		YYGML_array_set_owner((int64)(intptr_t)pSelf);
		YYRValue *__pArgs__[3];
		YYRValue __Args__[3];
		YYRValue __ret1__(0);

		FREE_RValue(&__ret1__);
		__Args__[2] = (*YY_GET_ARG(_args, (int)(1), _count));
		__pArgs__[2] = &__Args__[2];
		YYGML_CallMethod(pSelf, pOther, __ret1__, 1, (*YY_GET_ARG(_args, (int)(0), _count)), &__pArgs__[2]);

		delete threadArgs;
		return 0;
	}
};

#define RUN_IN_THREAD_BODY \
	SThreadArgs *threadArgs = new SThreadArgs(pSelf, pOther, _count, _args); \
	CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)&SCPU::ThreadFunc, threadArgs, 0, NULL)

#endif // __THREADING_HPP__

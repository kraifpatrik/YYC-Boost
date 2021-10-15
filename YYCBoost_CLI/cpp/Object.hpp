#ifndef __OBJECT_HPP__
#define __OBJECT_HPP__

#include "ArrayList.hpp"

// TODO: Registry needs to be locked when adding/getting values!

class CObject
{
public:
	CObject()
	{
		Id = GetRegistry().Add(this);
	}

	~CObject()
	{
		GetRegistry().Replace(Id, nullptr);
	}

	int GetId() const
	{
		return Id;
	}

	static CObject* FromId(int id)
	{
		CObject* o;
		if (GetRegistry().Get(id, &o))
		{
			return o;
		}
		return nullptr;
	}

private:
	static CArrayList<100, CObject*>& GetRegistry()
	{
		static CArrayList<100, CObject*> Registry;
		return Registry;
	}

	int Id;
};

// Note: Making FromId a template did not work
template<class C>
C* ObjectFromId(int id)
{
	return static_cast<C*>(CObject::FromId(id));
}

#endif // __OBJECT_HPP__

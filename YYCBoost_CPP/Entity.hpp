#pragma once

#include <string>

class CEntity
{
public:
	CEntity(std::string name)
		: Name(name)
	{
	}

	inline std::string GetName() const
	{
		return Name;
	}

	inline CEntity* GetParent() const
	{
		return Parent;
	}

private:
	std::string Name;

	class CEntity* Parent = nullptr;
};

#pragma once

#include "Entity.hpp"

class CVariable : CEntity
{
public:
	CVariable(std::string name, std::string type)
		: CEntity(name)
		, Type(type)
	{
	}

	inline std::string GetType() const
	{
		return Type;
	}

private:
	std::string Type;
};

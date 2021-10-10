#pragma once

#include "Entity.hpp"
#include <vector>

class CScope : CEntity
{
public:
	void AddChild(CEntity* child)
	{
		Children.push_back(child);
	}

private:
	std::vector<CEntity*> Children;
};

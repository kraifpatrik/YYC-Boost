#ifndef __ARRAY_LIST_HPP__
#define __ARRAY_LIST_HPP__

template<int S, typename T>
class CArrayList
{
public:
	~CArrayList()
	{
		if (Next)
		{
			delete Next;
		}
	}

	int Add(T v)
	{
		auto current = this;
		int index = 0;
		while (current->Index >= S)
		{
			if (!current->Next)
			{
				auto next = new CArrayList<S, T>();
				current->Next = next;
				next->Prev = current;
			}
			current = current->Next;
			index += S;
		}
		current->Values[current->Index] = v;
		return (index + current->Index++);
	}

	bool Get(int i, T* v)
	{
		CArrayList<S, T>* list;
		int index;
		if (FindCell(i, &list, &index))
		{
			*v = list->Values[index];
			return true;
		}
		return false;
	}

	bool Replace(int i, T v)
	{
		CArrayList<S, T>* list;
		int index;
		if (FindCell(i, &list, &index))
		{
			list->Values[index] = v;
			return true;
		}
		return false;
	}

private:
	bool FindCell(int i, CArrayList<S, T>** list, int* index)
	{
		auto current = this;
		while (current)
		{
			if (i >= S)
			{
				current = current->Next;
				i -= S;
			}
			else if (i >= current->Index)
			{
				return false;
			}
			else
			{
				*list = current;
				*index = i;
				return true;
			}
		}
		return false;
	}

	T Values[S];

	int Index = 0;

	CArrayList<S, T>* Prev = nullptr;

	CArrayList<S, T>* Next = nullptr;
};

#endif // __ARRAY_LIST_HPP__

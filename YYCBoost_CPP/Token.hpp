#pragma once

#include "TokenType.hpp"
#include <iostream>
#include <string>

struct SToken
{
    inline bool IsWhitespace() const
    {
        return (Type == ETokenType::WHITESPACE
            || Type == ETokenType::NEWLINE);
    }

    inline bool IsComment() const
    {
        return (Type == ETokenType::COMMENT
            || Type == ETokenType::DOCUMENTATION);
    }

    inline void Print() const
    {
        std::cout
            << "<\"" << Value << "\""
            << "; " << (size_t)Type
            << "; " << At
            << "; " << Length
            << ">";
    }

    std::string Value;

    ETokenType Type;

    size_t At = 0;

    size_t Length = 0;
};

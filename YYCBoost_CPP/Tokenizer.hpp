#pragma once

#include "Token.hpp"
#include <iostream>
#include <regex>
#include <string>
#include <vector>

#define RE_ARGS (std::regex_constants::ECMAScript | std::regex_constants::optimize)

#define RE_ARGS_ICASE (RE_ARGS | std::regex_constants::icase)

class CTokenizer
{
public:
	CTokenizer()
		// Reserved words
		: ReAll("all\\b", RE_ARGS)
		, ReBegin("begin\\b", RE_ARGS)
		, ReBreak("break\\b", RE_ARGS)
		, ReCase("case\\b", RE_ARGS)
		, ReCatch("catch\\b", RE_ARGS)
		, ReConstructor("constructor\\b", RE_ARGS)
		, ReContinue("continue\\b", RE_ARGS)
		, ReDefault("default\\b", RE_ARGS)
		, ReDelete("delete\\b", RE_ARGS)
		, ReDiv("div\\b", RE_ARGS)
		, ReDo("do\\b", RE_ARGS)
		, ReElse("else\\b", RE_ARGS)
		, ReEnd("end\\b", RE_ARGS)
		, ReEnum("enum\\b", RE_ARGS)
		, ReExit("exit\\b", RE_ARGS)
		, ReFalse("false\\b", RE_ARGS)
		, ReFinally("finally\\b", RE_ARGS)
		, ReFor("for\\b", RE_ARGS)
		, ReFunction("function\\b", RE_ARGS)
		, ReGlobal("global\\b", RE_ARGS)
		, ReIf("if\\b", RE_ARGS)
		, ReMod("mod\\b", RE_ARGS)
		, ReNew("new\\b", RE_ARGS)
		, ReNoone("noone\\b", RE_ARGS)
		, ReOther("other\\b", RE_ARGS)
		, ReRepeat("repeat\\b", RE_ARGS)
		, ReReturn("return\\b", RE_ARGS)
		, ReSelf("self\\b", RE_ARGS)
		, ReStatic("static\\b", RE_ARGS)
		, ReSwitch("switch\\b", RE_ARGS)
		, ReThrow("throw\\b", RE_ARGS)
		, ReTrue("true\\b", RE_ARGS)
		, ReTry("try\\b", RE_ARGS)
		, ReUntil("until\\b", RE_ARGS)
		, ReVar("var\\b", RE_ARGS)
		, ReWhile("while\\b", RE_ARGS)
		// Delimiters
		, ReUnderscore("_", RE_ARGS)
		, ReComma(",", RE_ARGS)
		, ReSemicolon(";", RE_ARGS)
		, ReColon(":", RE_ARGS)
		, ReExclamation("!", RE_ARGS)
		, ReAt("@", RE_ARGS)
		, ReSlash("/", RE_ARGS)
		, ReMinus("-", RE_ARGS)
		, ReQuestion("\\?", RE_ARGS)
		, ReDot("\\.", RE_ARGS)
		, ReBracketLeft("\\(", RE_ARGS)
		, ReBracketRight("\\)", RE_ARGS)
		, ReBracketSquareLeft("\\[", RE_ARGS)
		, ReBracketSquareRight("\\]", RE_ARGS)
		, ReBracketCurlyLeft("\\{", RE_ARGS)
		, ReBracketCurlyRight("\\}", RE_ARGS)
		, ReAsterisk("\\*", RE_ARGS)
		, ReBackslash("\\\\", RE_ARGS)
		, ReCaret("\\^", RE_ARGS)
		, RePlus("\\+", RE_ARGS)
		, RePipe("\\|", RE_ARGS)
		, ReDollar("\\$", RE_ARGS)
		, ReAmpersand("&", RE_ARGS)
		, ReHash("#", RE_ARGS)
		, RePercent("%", RE_ARGS)
		, ReLessThan("<", RE_ARGS)
		, ReEquals("=", RE_ARGS)
		, ReGreaterThan(">", RE_ARGS)
		, ReTilde("~", RE_ARGS)
		// Other
		, ReMacro("#macro\b", RE_ARGS)
		, ReDocumentation("/{3}[^\\n]*", RE_ARGS_ICASE)
		, ReCommentMultiline("/\\*(?:\\*[^/]|[^*])*\\*/", RE_ARGS_ICASE)
		, ReComment("//+[^\\n]*", RE_ARGS_ICASE)
		, ReName("[a-z_][a-z0-9_]*\\b", RE_ARGS_ICASE)
		, ReNumber("\\d+\\.?\\d*|\\.\\d+", RE_ARGS_ICASE)
		, ReStringMultiline("@\"(?:\\\"|[^\"])*\"", RE_ARGS_ICASE)
		, ReString("\"(?:\\\"|[^\"\\n])*\"", RE_ARGS_ICASE)
		, ReNewline("\\r?\\n", RE_ARGS_ICASE)
		, ReWhitespace("\\s+", RE_ARGS_ICASE)
	{
	}

	bool Tokenize(std::string code, std::vector<SToken>& tokens)
	{
		const char* ccode = code.c_str();
		size_t at = 0;

		while (ccode[at] != '\0')
		{
			SToken token;

			if (false
				// Reserved words
				|| GetToken(&ccode[at], ReAll, ETokenType::ALL, token)
				|| GetToken(&ccode[at], ReBegin, ETokenType::BRACKET_LEFT, token)  // BEGIN
				|| GetToken(&ccode[at], ReBreak, ETokenType::BREAK, token)
				|| GetToken(&ccode[at], ReCase, ETokenType::CASE, token)
				|| GetToken(&ccode[at], ReCatch, ETokenType::CATCH, token)
				|| GetToken(&ccode[at], ReConstructor, ETokenType::CONSTRUCTOR, token)
				|| GetToken(&ccode[at], ReContinue, ETokenType::CONTINUE, token)
				|| GetToken(&ccode[at], ReDefault, ETokenType::DEFAULT, token)
				|| GetToken(&ccode[at], ReDelete, ETokenType::DELETE, token)
				|| GetToken(&ccode[at], ReDiv, ETokenType::DIV, token)
				|| GetToken(&ccode[at], ReDo, ETokenType::DO, token)
				|| GetToken(&ccode[at], ReElse, ETokenType::ELSE, token)
				|| GetToken(&ccode[at], ReEnd, ETokenType::BRACKET_RIGHT, token)  // END
				|| GetToken(&ccode[at], ReEnum, ETokenType::ENUM, token)
				|| GetToken(&ccode[at], ReExit, ETokenType::EXIT, token)
				|| GetToken(&ccode[at], ReFalse, ETokenType::FALSE, token)
				|| GetToken(&ccode[at], ReFinally, ETokenType::FINALLY, token)
				|| GetToken(&ccode[at], ReFor, ETokenType::FOR, token)
				|| GetToken(&ccode[at], ReFunction, ETokenType::FUNCTION, token)
				|| GetToken(&ccode[at], ReGlobal, ETokenType::GLOBAL, token)
				|| GetToken(&ccode[at], ReIf, ETokenType::IF, token)
				|| GetToken(&ccode[at], ReMod, ETokenType::MOD, token)
				|| GetToken(&ccode[at], ReNew, ETokenType::NEW, token)
				|| GetToken(&ccode[at], ReNoone, ETokenType::NOONE, token)
				|| GetToken(&ccode[at], ReOther, ETokenType::OTHER, token)
				|| GetToken(&ccode[at], ReRepeat, ETokenType::REPEAT, token)
				|| GetToken(&ccode[at], ReReturn, ETokenType::RETURN, token)
				|| GetToken(&ccode[at], ReSelf, ETokenType::SELF, token)
				|| GetToken(&ccode[at], ReStatic, ETokenType::STATIC, token)
				|| GetToken(&ccode[at], ReSwitch, ETokenType::SWITCH, token)
				|| GetToken(&ccode[at], ReThrow, ETokenType::THROW, token)
				|| GetToken(&ccode[at], ReTrue, ETokenType::TRUE, token)
				|| GetToken(&ccode[at], ReTry, ETokenType::TRY, token)
				|| GetToken(&ccode[at], ReUntil, ETokenType::UNTIL, token)
				|| GetToken(&ccode[at], ReVar, ETokenType::VAR, token)
				|| GetToken(&ccode[at], ReWhile, ETokenType::WHILE, token)
				// Other
				|| GetToken(&ccode[at], ReMacro, ETokenType::MACRO, token)
				|| GetToken(&ccode[at], ReDocumentation, ETokenType::DOCUMENTATION, token)
				|| GetToken(&ccode[at], ReCommentMultiline, ETokenType::COMMENT, token)
				|| GetToken(&ccode[at], ReComment, ETokenType::COMMENT, token)
				|| GetToken(&ccode[at], ReName, ETokenType::NAME, token)
				|| GetToken(&ccode[at], ReNumber, ETokenType::NUMBER, token)
				|| GetToken(&ccode[at], ReStringMultiline, ETokenType::STRING, token)
				|| GetToken(&ccode[at], ReString, ETokenType::STRING, token)
				|| GetToken(&ccode[at], ReNewline, ETokenType::NEWLINE, token)
				|| GetToken(&ccode[at], ReWhitespace, ETokenType::WHITESPACE, token)
				// Delimiters
				|| GetToken(&ccode[at], ReUnderscore, ETokenType::UNDERSCORE, token)
				|| GetToken(&ccode[at], ReComma, ETokenType::COMMA, token)
				|| GetToken(&ccode[at], ReSemicolon, ETokenType::SEMICOLON, token)
				|| GetToken(&ccode[at], ReColon, ETokenType::COLON, token)
				|| GetToken(&ccode[at], ReExclamation, ETokenType::EXCLAMATION, token)
				|| GetToken(&ccode[at], ReAt, ETokenType::AT, token)
				|| GetToken(&ccode[at], ReSlash, ETokenType::SLASH, token)
				|| GetToken(&ccode[at], ReMinus, ETokenType::MINUS, token)
				|| GetToken(&ccode[at], ReQuestion, ETokenType::QUESTION, token)
				|| GetToken(&ccode[at], ReDot, ETokenType::DOT, token)
				|| GetToken(&ccode[at], ReBracketLeft, ETokenType::BRACKET_LEFT, token)
				|| GetToken(&ccode[at], ReBracketRight, ETokenType::BRACKET_RIGHT, token)
				|| GetToken(&ccode[at], ReBracketSquareLeft, ETokenType::BRACKET_SQUARE_LEFT, token)
				|| GetToken(&ccode[at], ReBracketSquareRight, ETokenType::BRACKET_SQUARE_RIGHT, token)
				|| GetToken(&ccode[at], ReBracketCurlyLeft, ETokenType::BRACKET_CURLY_LEFT, token)
				|| GetToken(&ccode[at], ReBracketCurlyRight, ETokenType::BRACKET_CURLY_RIGHT, token)
				|| GetToken(&ccode[at], ReAsterisk, ETokenType::ASTERISK, token)
				|| GetToken(&ccode[at], ReBackslash, ETokenType::BACKSLASH, token)
				|| GetToken(&ccode[at], ReCaret, ETokenType::CARET, token)
				|| GetToken(&ccode[at], RePlus, ETokenType::PLUS, token)
				|| GetToken(&ccode[at], RePipe, ETokenType::PIPE, token)
				|| GetToken(&ccode[at], ReDollar, ETokenType::DOLLAR, token)
				|| GetToken(&ccode[at], ReAmpersand, ETokenType::AMPERSAND, token)
				|| GetToken(&ccode[at], ReHash, ETokenType::HASH, token)
				|| GetToken(&ccode[at], RePercent, ETokenType::PERCENT, token)
				|| GetToken(&ccode[at], ReLessThan, ETokenType::LESS_THAN, token)
				|| GetToken(&ccode[at], ReEquals, ETokenType::EQUALS, token)
				|| GetToken(&ccode[at], ReGreaterThan, ETokenType::GREATER_THAN, token)
				|| GetToken(&ccode[at], ReTilde, ETokenType::TILDE, token)
			)
			{
				token.At = at;
				at += token.Length;
				tokens.push_back(token);
				continue;
			}

			return false;
		}

		return true;
	}

private:
	bool GetToken(const char* code, std::regex& re, ETokenType type, SToken& token)
	{
		std::cmatch m;

		if (std::regex_search(code, m, re, std::regex_constants::match_continuous))
		{
			token.Value = m.str();
			token.Type = type;
			token.Length = token.Value.size();
			return true;
		}

		return false;
	}

private:
	// Reserved words
	std::regex ReAll;
	std::regex ReBegin;
	std::regex ReBreak;
	std::regex ReCase;
	std::regex ReCatch;
	std::regex ReConstructor;
	std::regex ReContinue;
	std::regex ReDefault;
	std::regex ReDelete;
	std::regex ReDiv;
	std::regex ReDo;
	std::regex ReElse;
	std::regex ReEnd;
	std::regex ReEnum;
	std::regex ReExit;
	std::regex ReFalse;
	std::regex ReFinally;
	std::regex ReFor;
	std::regex ReFunction;
	std::regex ReGlobal;
	std::regex ReIf;
	std::regex ReMod;
	std::regex ReNew;
	std::regex ReNoone;
	std::regex ReOther;
	std::regex ReRepeat;
	std::regex ReReturn;
	std::regex ReSelf;
	std::regex ReStatic;
	std::regex ReSwitch;
	std::regex ReThrow;
	std::regex ReTrue;
	std::regex ReTry;
	std::regex ReUntil;
	std::regex ReVar;
	std::regex ReWhile;
	// Delimiters
	std::regex ReUnderscore;
	std::regex ReComma;
	std::regex ReSemicolon;
	std::regex ReColon;
	std::regex ReExclamation;
	std::regex ReAt;
	std::regex ReSlash;
	std::regex ReMinus;
	std::regex ReQuestion;
	std::regex ReDot;
	std::regex ReBracketLeft;
	std::regex ReBracketRight;
	std::regex ReBracketSquareLeft;
	std::regex ReBracketSquareRight;
	std::regex ReBracketCurlyLeft;
	std::regex ReBracketCurlyRight;
	std::regex ReAsterisk;
	std::regex ReBackslash;
	std::regex ReCaret;
	std::regex RePlus;
	std::regex RePipe;
	std::regex ReDollar;
	std::regex ReAmpersand;
	std::regex ReHash;
	std::regex RePercent;
	std::regex ReLessThan;
	std::regex ReEquals;
	std::regex ReGreaterThan;
	std::regex ReTilde;
	// Other
	std::regex ReMacro;
	std::regex ReDocumentation;
	std::regex ReCommentMultiline;
	std::regex ReComment;
	std::regex ReName;
	std::regex ReNumber;
	std::regex ReStringMultiline;
	std::regex ReString;
	std::regex ReNewline;
	std::regex ReWhitespace;
};

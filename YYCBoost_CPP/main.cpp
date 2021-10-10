#include "Token.hpp"
#include "Tokenizer.hpp"
#include <fstream>
#include <iostream>
#include <sstream>

int main(int argc, const char* argv[])
{
	std::ifstream file(argv[1]);
	std::stringstream buffer;
	buffer << file.rdbuf();
	std::string code = buffer.str();
	
	std::vector<SToken> tokens;
	CTokenizer tokenizer;
	tokenizer.Tokenize(code, tokens);

	return EXIT_SUCCESS;
}

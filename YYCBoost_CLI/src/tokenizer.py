# -*- coding: utf-8 -*-
import re
from enum import Enum, auto


class TokenizationError(Exception):
    pass


class Token(object):
    class Type(Enum):
        ALL = auto()
        AMPERSAND = auto()
        ASTERISK = auto()
        AT = auto()
        BACKSLASH = auto()
        # BEGIN = auto()
        BOOL = auto()
        BRACKET_CURLY_LEFT = auto()
        BRACKET_CURLY_RIGHT = auto()
        BRACKET_LEFT = auto()
        BRACKET_RIGHT = auto()
        BRACKET_SQUARE_LEFT = auto()
        BRACKET_SQUARE_RIGHT = auto()
        BREAK = auto()
        CARET = auto()
        CASE = auto()
        CATCH = auto()
        COLON = auto()
        COMMA = auto()
        COMMENT = auto()
        CONSTRUCTOR = auto()
        CONTINUE = auto()
        DEFAULT = auto()
        DELETE = auto()
        DIV = auto()
        DO = auto()
        DOCUMENTATION = auto()
        DOLLAR = auto()
        DOT = auto()
        ELSE = auto()
        # END = auto()
        ENUM = auto()
        EOF = auto()
        EQUALS = auto()
        EXCLAMATION = auto()
        EXIT = auto()
        FALSE = auto()
        FINALLY = auto()
        FOR = auto()
        FUNCTION = auto()
        GLOBAL = auto()
        GREATER_THAN = auto()
        HASH = auto()
        IF = auto()
        KEYWORD = auto()
        LESS_THAN = auto()
        MACRO = auto()
        MINUS = auto()
        MOD = auto()
        NAME = auto()
        NEW = auto()
        NEWLINE = auto()
        NOONE = auto()
        NUMBER = auto()
        OTHER = auto()
        PERCENT = auto()
        PIPE = auto()
        PLUS = auto()
        QUESTION = auto()
        REPEAT = auto()
        RETURN = auto()
        SELF = auto()
        SEMICOLON = auto()
        SLASH = auto()
        STATIC = auto()
        STRING = auto()
        SWITCH = auto()
        THROW = auto()
        TILDE = auto()
        TRUE = auto()
        TRY = auto()
        UNDEFINED = auto()
        UNDERSCORE = auto()
        UNTIL = auto()
        VAR = auto()
        WHILE = auto()
        WHITESPACE = auto()

    def __init__(self, _value: str, _type: int, _at: int, _len: int):
        self.value = _value
        self.type = _type
        self.at = _at
        self.len = _len

    def __repr__(self):
        return "<{}, {}, {}, {}>".format(
            repr(self.value),
            self.type,
            self.at,
            self.len)

    def is_whitespace(self):
        return self.type in [Token.Type.WHITESPACE, Token.Type.NEWLINE]

    def is_comment(self):
        return self.type in [Token.Type.COMMENT, Token.Type.DOCUMENTATION]


RESERVED = {
    "all": Token.Type.ALL,
    "begin": Token.Type.BRACKET_LEFT,  # Token.Type.BEGIN
    "break": Token.Type.BREAK,
    "case": Token.Type.CASE,
    "catch": Token.Type.CATCH,
    "constructor": Token.Type.CONSTRUCTOR,
    "continue": Token.Type.CONTINUE,
    "default": Token.Type.DEFAULT,
    "delete": Token.Type.DELETE,
    "div": Token.Type.DIV,
    "do": Token.Type.DO,
    "else": Token.Type.ELSE,
    "end": Token.Type.BRACKET_RIGHT,  # Token.Type.END
    "enum": Token.Type.ENUM,
    "exit": Token.Type.EXIT,
    "false": Token.Type.FALSE,
    "finally": Token.Type.FINALLY,
    "for": Token.Type.FOR,
    "function": Token.Type.FUNCTION,
    "global": Token.Type.GLOBAL,
    "if": Token.Type.IF,
    "mod": Token.Type.MOD,
    "new": Token.Type.NEW,
    "noone": Token.Type.NOONE,
    "other": Token.Type.OTHER,
    "repeat": Token.Type.REPEAT,
    "return": Token.Type.RETURN,
    "self": Token.Type.SELF,
    "static": Token.Type.STATIC,
    "switch": Token.Type.SWITCH,
    "throw": Token.Type.THROW,
    "true": Token.Type.TRUE,
    "try": Token.Type.TRY,
    "until": Token.Type.UNTIL,
    "var": Token.Type.VAR,
    "while": Token.Type.WHILE,
}


DELIMITERS = {
    r"_": Token.Type.UNDERSCORE,
    r",": Token.Type.COMMA,
    r";": Token.Type.SEMICOLON,
    r":": Token.Type.COLON,
    r"!": Token.Type.EXCLAMATION,
    r"@": Token.Type.AT,
    r"/": Token.Type.SLASH,
    r"\-": Token.Type.MINUS,
    r"\?": Token.Type.QUESTION,
    r"\.": Token.Type.DOT,
    r"\(": Token.Type.BRACKET_LEFT,
    r"\)": Token.Type.BRACKET_RIGHT,
    r"\[": Token.Type.BRACKET_SQUARE_LEFT,
    r"\]": Token.Type.BRACKET_SQUARE_RIGHT,
    r"\{": Token.Type.BRACKET_CURLY_LEFT,
    r"\}": Token.Type.BRACKET_CURLY_RIGHT,
    r"\*": Token.Type.ASTERISK,
    r"\\": Token.Type.BACKSLASH,
    r"\^": Token.Type.CARET,
    r"\+": Token.Type.PLUS,
    r"\|": Token.Type.PIPE,
    r"\$": Token.Type.DOLLAR,
    r"&": Token.Type.AMPERSAND,
    r"#": Token.Type.HASH,
    r"%": Token.Type.PERCENT,
    r"<": Token.Type.LESS_THAN,
    r"=": Token.Type.EQUALS,
    r">": Token.Type.GREATER_THAN,
    r"~": Token.Type.TILDE,
}

REGEX_CACHE = {}

class Tokenizer(object):
    def tokenize(self, _code: str):
        tokens = []
        at = 0

        def get_token(_regex, _type):
            if _regex in REGEX_CACHE:
                r = REGEX_CACHE[_regex]
            else:
                r = re.compile(_regex, flags=re.IGNORECASE)
                REGEX_CACHE[_regex] = r

            m = r.match(_code)
            if m:
                _start = m.start(0)
                _len = m.end(0)
                token = Token(m.group(0), _type, at + _start, _len - _start)
                return token
            return None

        while _code:
            token = None

            for k, v in RESERVED.items():
                token = get_token(r"^" + k + r"\b", v)
                if token:
                    break

            if not token:
                token = (get_token(r"^#macro\b", Token.Type.MACRO) or
                         get_token(r"^\/{3}[^\n]*", Token.Type.DOCUMENTATION) or
                         get_token(r"^\/\*(?:\*[^/]|[^*])*\*\/", Token.Type.COMMENT) or
                         get_token(r"^\/\/+[^\n]*", Token.Type.COMMENT) or
                         get_token(r"^[a-z_][a-z0-9_]*", Token.Type.NAME) or
                         get_token(r"^\d+\.?\d*|\.\d+", Token.Type.NUMBER) or
                         get_token(r"^\$[a-f0-9]+", Token.Type.NUMBER) or
                         get_token(r"^@\"(?:\\.|[^\\\"])*\"", Token.Type.STRING) or
                         get_token(r"^\"(?:\\.|[^\\\"\n])*\"", Token.Type.STRING) or
                         get_token(r"^\r?\n", Token.Type.NEWLINE) or
                         get_token(r"^\s+", Token.Type.WHITESPACE))

                if token and token.type == Token.Type.DOCUMENTATION:
                    if re.match(r"^\/{4,}$", token.value):
                        token.type = Token.Type.COMMENT

            if not token:
                for k, v in DELIMITERS.items():
                    token = get_token(r"^" + k, v)
                    if token:
                        break

            if token:
                tokens.append(token)
                _code = _code[token.len:]
                at += token.len
            else:
                raise TokenizationError()

        tokens.append(Token("", Token.Type.EOF, at, 0))

        return tokens

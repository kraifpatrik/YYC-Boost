# -*- coding: utf-8 -*-
import re

from .tokenizer import Token


class Entity(object):
    def __init__(self, _name=""):
        self.name = _name
        self.parent = None


class Macro(Entity):
    pass


class Member(Entity):
    pass


class Variable(Entity):
    def __init__(self, **kwargs):
        super(Variable, self).__init__(**kwargs)
        self.type = None


class Scope(Entity):
    def __init__(self, **kwargs):
        super(Scope, self).__init__(**kwargs)
        self.children = []
        self.code = ""

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def get_children(self, _type=None, _name=None):
        children = []
        for c in self.children:
            if _type != None and not isinstance(c, _type):
                continue
            if _name != None and not c.name != _name:
                continue
            children.append(c)
        children.sort(key=lambda c: c.name)
        return children

    def __repr__(self):
        def _print(entity, indent):
            s = (" " * indent * 4) + "* " + \
                (entity.name if entity.name else "<anonymous>") + \
                " ({}) ".format(type(entity).__name__) + "\n"
            if isinstance(entity, Scope):
                for c in entity.children:
                    s += _print(c, indent + 1)
            return s
        return _print(self, 0)


class Object(Scope):
    pass


class Script(Scope):
    pass


class Function(Scope):
    pass


class Constructor(Function):
    pass


class Enum(Scope):
    pass


class Tag(object):
    def __init__(self, _tag, _type=None, _name=None, _desc=""):
        self.tag = _tag
        self.type = _type
        self.name = _name
        self.desc = _desc

    def __repr__(self):
        return str({
            "tag": self.tag,
            "type": self.type,
            "name": self.name,
            "desc": self.desc,
        })


class Documentation(object):
    def __init__(self):
        self.tags = {}

    def __repr__(self):
        return str(self.tags)

    def add_tag(self, tag):
        tagname = tag.tag
        if not tagname in self.tags:
            self.tags[tagname] = []
        self.tags[tagname].append(tag)

    def get_tag(self, tag, single=True):
        tags = self.tags.get(tag, [])
        if single:
            if len(tags) == 0:
                return None
            return tags[0]
        return tags

    @staticmethod
    def from_string(_str):
        docs = Documentation()

        _str = _str.split("\n")
        _str = "\n".join(
            list(map(lambda l: re.sub(r"^\s*///", "", l, count=1), _str)))

        # Handle links
        _str = re.sub(r"\{@link ([^\}]+)\}", "[\\1](\\1.html)", _str)

        while True:
            # Tag
            m = re.match(r"\s*@([a-z]+)", _str)
            if not m:
                break

            tag = m.group(1)
            _str = _str[m.end(0):]

            # Optional type
            m = re.match(r"\s*\{([^\}]*)\}", _str)
            if m:
                typestr = m.group(1)
                _str = _str[m.end(0):]
            else:
                typestr = None

            # Param name
            name = None
            if tag == "param":
                m = re.match(r"\s*\[?([a-z_]+[a-z0-9_]*)\]?",
                             _str, flags=re.IGNORECASE)
                if m:
                    name = m.group(1)
                    _str = _str[m.end(0):]

            # Description
            s = re.search(r"(?<!/// )@[a-z]+", _str)
            end = s.start(0) if s else len(_str)
            desc = _str[:end].strip()

            # Handle markdown code
            split = desc.split("```")
            for i in range(len(split)):
                if i % 2:
                    # TODO: Delete spaces based on indent of opening ```
                    split[i] = re.sub(r"\n ", "\n", split[i])
                else:
                    split[i] = "\n" + \
                        re.sub(r"\s+", " ", split[i]).strip() + "\n"
            desc = "```".join(split).strip()

            docs.add_tag(Tag(tag, typestr, name, desc))

            _str = _str[end:]

        return docs


class Parser(object):
    def __init__(self, tokens):
        self.index = 0
        self.tokens = tokens

    def mark(self):
        return (self.index,)

    def reset(self, _mark):
        self.index = _mark[0]

    def available(self):
        return len(self.tokens) - self.index

    def peek(self):
        return self.tokens[self.index]

    def next(self):
        token = self.tokens[self.index]
        self.index += 1
        return token

    def consume(self, _value=None, _type=None, _ignore_whitespace=True, _ignore_comments=True):
        mark = self.mark()
        while self.available():
            token = self.next()
            if _ignore_whitespace and token.is_whitespace():
                continue
            if _ignore_comments and token.is_comment():
                continue
            if _value != None and token.value != _value:
                self.reset(mark)
                return None
            if _type != None and token.type != _type:
                self.reset(mark)
                return None
            return token
        self.reset(mark)
        return None

    def find(self, _value=None, _type=None):
        mark = self.mark()
        while self.available():
            token = self.next()
            if _value != None and token.value != _value:
                continue
            if _type != None and token.type != _type:
                continue
            return token
        self.reset(mark)
        return None

    def _parse_function(self, _method=False):
        # TODO: Mark and reset on errors

        if not self.consume(_type=Token.Type.FUNCTION):
            return None

        name = self.consume(_type=Token.Type.NAME)
        self.consume(_type=Token.Type.BRACKET_LEFT)

        bracket_counter = 1
        while True:
            peek = self.peek()
            if peek.type == Token.Type.BRACKET_LEFT:
                bracket_counter += 1
            elif peek.type == Token.Type.BRACKET_RIGHT:
                bracket_counter -= 1
                if bracket_counter == 0:
                    break
            self.next()

        self.consume(_type=Token.Type.BRACKET_RIGHT)

        # Super constructor
        if self.consume(_type=Token.Type.COLON):
            self.consume(_type=Token.Type.NAME)
            self.consume(_type=Token.Type.BRACKET_LEFT)

            bracket_counter = 1
            while True:
                peek = self.peek()
                if peek.type == Token.Type.BRACKET_LEFT:
                    bracket_counter += 1
                elif peek.type == Token.Type.BRACKET_RIGHT:
                    bracket_counter -= 1
                    if bracket_counter == 0:
                        break
                self.next()

            self.consume(_type=Token.Type.BRACKET_RIGHT)

        constructor = self.consume(_type=Token.Type.CONSTRUCTOR)

        self.consume(_type=Token.Type.BRACKET_CURLY_LEFT)

        if constructor:
            return Constructor(_name=name.value if name else None)

        return Function(_name=name.value if name else None)

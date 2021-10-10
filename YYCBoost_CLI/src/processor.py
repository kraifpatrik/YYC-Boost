from ast import parse
import os
import re

from .tokenizer import *
from .parser import *


REGEX_ANON = re.compile(r"extern YYVAR g_Script_(gml_(?:Script|Object)_\w+)")

counter = 0

class Processor(object):
    INCLUDES = """#include "YYCBoost.h"\n"""

    @staticmethod
    def inject_type(cpp_content, name, type_):
        global counter

        name_cpp = f"local_{name}"

        # Replace type
        cpp_content = cpp_content.replace(
            f"YYRValue {name_cpp}",
            f"{type_} {name_cpp}")

        # Passing as arguments
        while True:
            m = re.search(
                r"&\s*/\*\s*local\s*\*/\s*{}".format(name_cpp), cpp_content)
            if not m:
                break
            name_ref = f"__native_ref{counter}__"
            span = m.span()
            cpp_content = cpp_content[:span[0]] + "&" + \
                name_ref + cpp_content[span[1]:]
            idx = cpp_content.rfind("\n", 0, span[0])
            idx = 0 if idx == -1 else idx
            cpp_content = cpp_content[:idx] + "\nYYRValue {}({});".format(
                name_ref, name_cpp) + cpp_content[idx:]
            counter += 1

        # Remove casts
        cpp_content = re.sub(
            r"{}\.as\w+\(\)".format(name_cpp), name_cpp, cpp_content)

        if type_ == "bool":
            cpp_content = re.sub(
                r"BOOL_RValue\(.*{}[^)]*\)".format(name_cpp), name_cpp, cpp_content)

        return cpp_content

    @staticmethod
    def inject_code(cpp_path, gml_path):
        cpp_basename = os.path.basename(cpp_path)

        with open(gml_path, "r") as f:
            gml_content = f.read()

        tokens = Tokenizer().tokenize(gml_content)

        parser = Parser(tokens)

        current = Script(_name=cpp_path) if "GlobalScript" in cpp_path \
            else Object(_name=re.sub(r"gml_Object_[^_]+_", "", cpp_basename)[:-8])
        root = current

        while parser.available():
            token = parser.peek()

            if token.type == Token.Type.FUNCTION:
                func = parser._parse_function()
                current.add_child(func)
                current = func
                continue

            # if token.type == Token.Type.BRACKET_CURLY_LEFT:
            #     scope = Scope()
            #     current.add_child(scope)
            #     current = scope
            #     continue

            if token.type == Token.Type.BRACKET_CURLY_LEFT:
                parser.next()
                scope = Scope()
                current.add_child(scope)
                current = scope
                continue

            if token.type == Token.Type.BRACKET_CURLY_RIGHT:
                parser.next()
                current = current.parent
                continue

            if token.type == Token.Type.COMMENT:
                parser.next()
                if token.value.startswith("/*cpp"):
                    current.code += token.value[5:-2].strip() + "\n"
                continue

            if token.type == Token.Type.VAR:
                parser.next()
                name = parser.consume(_type=Token.Type.NAME)
                if name is None:
                    continue
                comment = parser.consume(_type=Token.Type.COMMENT, _ignore_comments=False)
                if comment is None:
                    continue
                if not comment.value.startswith("/*:"):
                    continue
                _var = Variable(_name=name.value)
                _var.type = comment.value[3:-2].strip()
                current.add_child(_var)
                continue

            parser.next()

        ########################################################################
        with open(cpp_path, "r") as f:
            cpp_content = f.read()

        anon_names = REGEX_ANON.findall(cpp_content)

        matched = []

        def _match_anon(scope):
            nonlocal matched

            if isinstance(scope, Scope):
                for child in scope.children:
                    _match_anon(child)

            if isinstance(scope, Function) or isinstance(scope, Object):
                matched.append({
                    "func": scope,
                    "name": anon_names.pop(0),
                })

        _match_anon(root)

        for m in matched:
            _name = m["name"]
            _func = m["func"]

            is_function = isinstance(_func, Function)

            # Find func. body
            if is_function:
                head = re.escape(f"YYRValue& {_name}( CInstance* pSelf, CInstance* pOther, YYRValue& _result, int _count,  YYRValue** _args  )") + \
                    r"\n+\{"
            else:
                head = re.escape(f"void {_name}( CInstance* pSelf, CInstance* pOther )") + \
                    r"\n+\{"

            start = re.search(head, cpp_content)
            if start is None:
                raise Exception(f"Could not find {head}!")
            start = start.end()
            count = 1
            index = start
            while True:
                if cpp_content[index] == "{":
                    count += 1
                elif cpp_content[index] == "}":
                    count -= 1
                    if count == 0:
                        end = index
                        break
                index += 1

            _code = _func.code
            if _code != "":
                # Replace body with C++
                cpp_before = cpp_content[:start]
                cpp_after = cpp_content[end:]
                cpp_content = cpp_before + "\n"

                if is_function:
                    cpp_content += \
                        f"""YY_STACKTRACE_FUNC_ENTRY( "{_name}", 0 );\n""" + \
                        "YYGML_array_set_owner( (int64)(intptr_t)pSelf );\n"

                cpp_content += _code

                if is_function:
                    cpp_content += "_result = 0;\nreturn _result;\n"

                cpp_content += cpp_after

            else:
                # Inject types into local vars
                def _inject_type(scope):
                    nonlocal cpp_content
                    for child in scope.children:
                        if type(child) == Scope:
                            _inject_type(child)
                            continue
                        if not isinstance(child, Variable):
                            continue
                        name = child.name
                        type_ = child.type

                        cpp_content = cpp_content[:start] + \
                            Processor.inject_type(cpp_content[start:end], name, type_) + \
                            cpp_content[end:]
                _inject_type(_func)

        if not cpp_content.startswith(Processor.INCLUDES):
            cpp_content = Processor.INCLUDES + cpp_content

        with open(cpp_path, "w") as f:
            f.write(cpp_content)

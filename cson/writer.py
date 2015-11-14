import re
import json
from numbers import Number
from math import floor, isinf

SPACES = " " * 10


try:
    xrange
    range = xrange
except:
    pass

try:
    basestring
except:
    basestring = (str, bytes)


def newline_wrap(s):
    return "\n%s\n" % s


def is_dict(x):
    return isinstance(x, dict)


def is_undefined(x):
    return x is None


def isfinite(x):
    return not isinf(x)


identifier_pattern = re.compile(ur"^[a-z_$][a-z0-9_$]*$", re.IGNORECASE)


is_function = callable


def stringify(data, indent=2):
    if is_undefined(data) or is_function(data):
        return None
    if isinstance(indent, basestring):
        indent = indent[0:10]
    elif isinstance(indent, Number):
        n = min(10, floor(indent))
        n = 0 if n not in range(1, 10) else n
        indent = SPACES[:int(n)]

    normalized = json.loads(json.dumps(data))

    def indent_line(line):
        return indent + line

    def indent_lines(lines):
        return '\n'.join(map(indent_line, lines.split("\n")))

    def visit_string(s, **options):
        if s.find("\n") == -1 or not indent:
            return json.dumps(s)
        else:
            s = re.sub(
                r"'''", r"\\'''",
                re.sub(r"\\", r"\\\\", s))
            return u"'''%s'''" % newline_wrap(indent_lines(s))

    visit_list = None
    visit_dict = None

    def visit_node(node, **options):
        if isinstance(node, bool):
            return json.dumps(node)
        elif isinstance(node, Number):
            if isfinite(node):
                return u"%d" % node
            else:
                return u'null'
        elif isinstance(node, basestring):
            return visit_string(node, **options)
        elif isinstance(node, list):
            return visit_list(node, **options)
        elif isinstance(node, dict):
            return visit_dict(node, **options)
        elif node is None:
            return u"null"
        else:
            raise Exception("Don't know how to deal with %r" % node)

    def visit_list(lst, **options):
        items = [visit_node(i, braces_required=True) for i in lst]
        if indent:
            serialized = newline_wrap(indent_lines('\n'.join(items)))
        else:
            serialized = u', '.join(items)
        return u"[ %s ]" % serialized

    def visit_dict(dct, braces_required=False, **options):
        keypairs = []
        for key, value in dct.items():
            key = key if identifier_pattern.match(key) else json.dumps(key)
            serialized_value = visit_node(value, braces_required=not indent)
            if indent:
                if isinstance(value, dict) and len(value) > 0:
                    serialized_value = "\n %s " % indent_lines(serialized_value)
            keypairs.append("%s: %s" % (key, serialized_value))
        if len(keypairs) == 0:
            return u"{}"
        elif indent:
            serialized_keypairs = '\n'.join(keypairs)
            if braces_required:
                return u"{%s}" % newline_wrap(indent_lines(serialized_keypairs))
            else:
                return serialized_keypairs
        else:
            serialized_keypairs = u', '.join(keypairs)
            if braces_required:
                return u"{%s}" % serialized_keypairs
            else:
                return serialized_keypairs

    return visit_node(normalized)

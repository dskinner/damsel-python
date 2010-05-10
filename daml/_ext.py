# -*- coding: utf-8 -*-
from _pre_parse import _pre_parse
from _py_parse import _py_parse
import _sandbox

def include(f):
    f = open(f).readlines()
    f = _pre_parse(f)
    f = _py_parse(f)
    return f

def block(s):
    s = s.splitlines()
    s = _py_parse(s)
    globals()['__blocks__'][s[0]] = [s[1:], False] # [content, been-used-yet?]

extensions = {  'include': include,
                'block': block}

_sandbox.default_sandbox.update(extensions)


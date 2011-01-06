#! /usr/bin/env python
# -*- coding: utf-8 -*-
from copy import copy
from lxml import etree

import _sandbox
from _pre import _pre
from _py import _py, _compile
from _doc import _doc, _doc_pre, _doc_build

class Template(object):
    def __init__(self, filename):
        if isinstance(filename, list):
            self.f = filename
        else:
            self.f = _sandbox._open(filename).read().splitlines()
        self.r, self.q = _pre(self.f)
        self.sandbox = _sandbox.new()
        self.code = _compile(self.q)
        self.r = _doc_pre(self.r)
    
    def render(self, context={}):
        s = copy(self.sandbox)
        s.update(context)
        py = _py(self.r, self.q, s, code=self.code)
        b = _doc_build(_doc_pre(py))
        return _post(etree.tostring(b))

def _post(s):
    return '<!DOCTYPE html>'+s.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')

def parse(_f, context={}):
    f = _sandbox._open(_f).read().splitlines()
    sandbox = _sandbox.new()
    sandbox.update(context)
    r, q = _pre(f)
    py = _py(r, q, sandbox)
    b = _doc(py)
    return _post(etree.tostring(b))

if __name__ == '__main__':
    import sys
    import codecs
    from time import time
    _f = sys.argv[1]
    print parse(_f)


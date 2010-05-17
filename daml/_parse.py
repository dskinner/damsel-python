#! /usr/bin/env python
# -*- coding: utf-8 -*-
from _pre_parse import _pre_parse
import _py_parse
from _doc_parse import _doc_parse
from _build import _build
import _sandbox
from lxml import etree

def _post(s):
    return '<!DOCTYPE html>'+s.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')

def parse(f, context={}):
    _py_parse.sandbox = _sandbox.new()
    _py_parse.sandbox.update(_py_parse.ext)
    _py_parse.sandbox.update(context)
    f = _pre_parse(f)
    f = _py_parse._py_parse(f)
    f = _doc_parse(f)
    #f = _build(f)

    return _post(etree.tostring(f))

if __name__ == '__main__':
    import sys
    import codecs
    f = sys.argv[1]
    f = codecs.open(f, 'r', encoding='utf-8').read().splitlines()
    print parse(f)
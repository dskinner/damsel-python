#! /usr/bin/env python
# -*- coding: utf-8 -*-
from _pre_parse import _pre_parse
import _py_parse
from _doc_parse import _doc_parse
from _build import _build
import _sandbox
from lxml import etree

def _post(s):
    """
    For now, should look for html tags embedded in Element.text and
    Element.tail with some sort of marker that says to unescape this.
    This can be done after tostring maybe with a find/replace or it
    could be done before tostring and create proper Element's adjusting
    head/tail text and appending as necessary. Im guessing the latter
    would be slower.

    NOTE this cant be done post-processor after tostring, theres no way to
    know when something was marked safe.
    """
    return '<!DOCTYPE html>'+s.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')

def parse(f, context={}):
    _py_parse.sandbox = _sandbox.new()
    _py_parse.sandbox.update(_py_parse.ext)
    _py_parse.sandbox.update(context)
    f = _pre_parse(f)
    f = _py_parse._py_parse(f)
    f = _doc_parse(f)
    f = _build(f)
    
    return _post(etree.tostring(f[0][1]))

if __name__ == '__main__':
    import sys
    import codecs
    f = sys.argv[1]
    f = codecs.open(f, 'r', encoding='utf-8').read().splitlines()
    print parse(f)
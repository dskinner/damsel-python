#! /usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree

import _sandbox
from _ext import extensions
from _parse_pre import _parse_pre
from _parse_py import _parse_py
from _parse_doc import _parse_doc

from _c_parse_pre import _parse_pre as _c_parse_pre
from _c_parse_py import _parse_py as _c_parse_py
from _c_parse_doc import _parse_doc as _c_parse_doc

def _post(s):
    return '<!DOCTYPE html>'+s.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')

def parse(_f, context={}):
    f = _sandbox._open(_f).read().splitlines()
    sandbox = _sandbox.new()
    sandbox.update(extensions)
    sandbox.update(context)
    r, q = _parse_pre(f)
    py = _parse_py(r, q, sandbox)
    b = _parse_doc(py)
    return _post(etree.tostring(b))

def c_parse(_f, context={}):
    f = _sandbox._open(_f).read().splitlines()
    sandbox = _sandbox.new()
    sandbox.update(extensions)
    sandbox.update(context)
    r, q = _c_parse_pre(f)
    py = _c_parse_py(r, q, sandbox)
    b = _c_parse_doc(py)
    return _post(etree.tostring(b))

if __name__ == '__main__':
    import sys
    import codecs
    from time import time
    _f = sys.argv[1]
    
    try:
        option = sys.argv[2]
        if option == 'c':
            p = c_parse
        else:
            p = parse
        
        times=[]
        for x in range(100):
            a = time()
            r = p(_f)
            times.append(time()-a)
        print min(times)
    except IndexError:
        print parse(_f)
    except Exception as e:
        c_parse(_f)
        



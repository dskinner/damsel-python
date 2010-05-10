#! /usr/bin/env python
# -*- coding: utf-8 -*-
from _pre_parse import _pre_parse
from _py_parse import _py_parse, sandbox
from _doc_parse import _doc_parse
from _build import _build
from lxml import etree

def parse(f, context={}):
    sandbox.update(context)
    f = _pre_parse(f)
    f = _py_parse(f)
    f = _doc_parse(f)
    f = _build(f)
    
    return etree.tostring(f[0][1])

if __name__ == '__main__':
    import sys
    f = sys.argv[1]
    f = open(f).readlines()
    print parse(f)
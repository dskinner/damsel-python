#! /usr/bin/env python
# -*- coding: utf-8 -*-
from lxml import etree

def bench(f):
    f = _pre_parse(f)
    f = _py_parse(f)
    f = _doc_parse(f)
    f = _build(f)
    etree.tostring(f[0][1])

if __name__ == '__main__':
    from time import time
    from _pre_parse import _pre_parse
    from _py_parse import _py_parse
    from _doc_parse import _doc_parse
    from _build import _build
    import sys
    from lxml import etree

    _f = sys.argv[1]
    f = open(_f).readlines()
    
    times = []
    for x in range(200):
        a = time()
        bench(f)
        times.append(time()-a)
    print(min(times))
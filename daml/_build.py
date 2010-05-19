#! /usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree

def _build(parsed):
    """
    As tags indent, it is easy to identify the parent. It is simply the last
    element processed. If indention is the same, it is simply the last elements
    parent.

    While processing this data, we can record a dict indexed by indention. When
    a tag decreases in indention, I think it is safe to assume that it will
    fall on a pre-existing indention level. This will trigger a lookup in the
    dict and get the parent of that element. Afterwards, we clean up the dict
    to remove all keys with an indention level higher then the decreased one so
    future elements do not get appended to incorrect items if variable
    indention is used.
    """
    r = parsed
    m = {}

    prev = parsed[0][0]
    for i, d in enumerate(parsed):
        if i is 0:
            continue

        ws = d[0]

        if ws > prev:
            r[i-1][1].append(r[i][1])   # ('    ', Element)[1].append(...)
            m[ws] = i
        elif ws == prev:
            r[i-1][1].getparent().append(r[i][1])
            m[ws] = i
        elif ws < prev:
            j = m[ws]
            r[j][1].getparent().append(r[i][1])
            # purge mapping of larger indents then this unindent
            for k in m.keys():
                if k > ws:
                    m.pop(k)
            m[ws] = i
        prev = ws
    return r

if __name__ == '__main__':
    from _pre_parse import _pre_parse
    import _py_parse
    #from _doc_parse import _doc_parse
    from _cext import _doc_parse
    from _parse import parse, _post
    import _sandbox
    import sys
    from lxml import etree
    from time import time
    import codecs

    sys_f = sys.argv[1]
    _f = codecs.open(sys_f, 'r', encoding='utf-8').read().splitlines()
    t = sys.argv[2]

    if t == 'y':
        init_times = []
        pre_times = []
        py_times = []
        doc_times = []
        build_times = []
        tostring_times = []
        post_times = []

        for x in range(10):
            a = time()
            _py_parse.sandbox = _sandbox.new()
            _py_parse.sandbox.update(_py_parse.ext)
            init_times.append(time()-a)

            a = time()
            f = _pre_parse(_f)
            pre_times.append(time()-a)

            a = time()
            f = _py_parse._py_parse(f)
            py_times.append(time()-a)

            a = time()
            f = _doc_parse(f)
            doc_times.append(time()-a)
            '''
            a = time()
            f = _build(f)
            build_times.append(time()-a)
            '''
            a = time()
            s = etree.tostring(f)
            tostring_times.append(time()-a)

            a = time()
            s = _post(s)
            post_times.append(time()-a)

        print 'init', min(init_times)
        print '_pre_parse', min(pre_times)
        print '_py_parse ', min(py_times)
        print '_doc_parse', min(doc_times)
        #print '_build    ', min(build_times)
        print 'tostring  ', min(tostring_times)
        print '_post     ', min(post_times)
        #print s
    elif t == 'a':
        times = []
        for x in range(2000):

            a = time()

            _py_parse.sandbox = _sandbox.new()
            _py_parse.sandbox.update(_py_parse.ext)

            f = _pre_parse(_f)
            f = _py_parse._py_parse(f)
            f = _doc_parse(f)
            s = etree.tostring(f)
            s = _post(s)
            times.append(time()-a)
        print min(times)
    elif t == 'p':
        times = []
        for x in range(2000):
            a = time()
            parse(_f)
            times.append(time()-a)
        print min(times)
    else:
        print parse(_f)


#! /usr/bin/env python
# -*- coding: utf-8 -*-

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
    more = 0
    same = 0
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
    from _py_parse import _py_parse
    from _doc_parse import _doc_parse
    from _parse import parse
    import sys
    from lxml import etree
    from time import time

    _f = sys.argv[1]
    _f = open(_f).readlines()
    t = sys.argv[2]

    if t == 'y':
        times = []
        for x in range(2000):
            a = time()
            parse(_f)
            times.append(time()-a)
        print min(times)
    else:
        print parse(_f)


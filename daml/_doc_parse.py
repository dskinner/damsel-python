#! /usr/bin/env python
# -*- coding: utf-8 -*-
from lxml.etree import Element, SubElement
from collections import deque

from _cext import parse_ws, parse_attr, parse_tag, split_space

def _doc_parse(f):
    r = [('', Element('html'))]
    plntxt = deque()

    prev = ''

    for line in f[1:]:
        ws, l = parse_ws(line)

        if l[0] not in ['%', '#', '.']:
            plntxt.append((ws, l))
            continue

        # check plntxt queue
        # everything in queue should be same indention width
        # since nowhere in a doc should there be plain text indented to plain text
        #for x in plntxt:

        while plntxt:
            _ws, text = plntxt.popleft()
            j = -1
            while j:
                if _ws > r[j][0]:
                    r[j][1].text += ' '+text
                    break
                elif _ws == r[j][0]:
                    if r[j][1].tail is None: # faster than init'ing tail on element creation everytime
                        r[j][1].tail = text
                    else:
                        r[j][1].tail += ' '+text
                    break
                j -= 1

        # determine tag attributes
        u, attr = parse_attr(l)
        u = split_space(u)

        _tag, _id, _class = parse_tag(u[0])
        #
        if ws > prev:
            e_root = r[-1][1]
        if ws == prev:
            e_root = r[-1][1].getparent()
        if ws < prev:
            j = -1
            while j:
                if r[j][0] == ws:
                    e_root = r[j][1].getparent()
                    break
                j -= 1
        prev = ws

        e = SubElement(e_root, _tag or 'div')
        e.text = u[1][1:]

        if _id:
            e.attrib['id'] = _id

        if _class:
            e.attrib['class'] = _class

        if attr:
            for x in attr[1:-1].split(','):
                k, tmp, v = x.partition('=')
                e.attrib[k.strip()] = v.strip()

        r.append((ws, e))
    return r[0][1]


if __name__ == '__main__':
    from _pre_parse import _pre_parse
    from _py_parse import _py_parse
    import sys
    from time import time

    _f = sys.argv[1]
    _f = open(_f).readlines()
    t = sys.argv[2]

    if t == 'y':
        times = []
        for x in range(2000):
            a = time()
            f = _pre_parse(_f)
            f = _py_parse(f)
            f = _doc_parse(f)
            times.append(time()-a)
        print min(times)
    else:
        f = _pre_parse(_f)
        f = _py_parse(f)
        f = _doc_parse(f)

        for x in f:
            print `x`


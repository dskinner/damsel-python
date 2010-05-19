#! /usr/bin/env python
# -*- coding: utf-8 -*-
from lxml.etree import Element, SubElement


def _doc_parse(f):
    r = {'': Element('html')}
    plntxt = {}

    prev = ''

    for line in f[1:]:
        ws, l = parse_ws(line)

        ### plntxt queue
        if not_directive(l[0]):
            if ws in plntxt:
                plntxt[ws].append(l)
            else:
                plntxt[ws] = [l]
            continue

        if plntxt:
            for _ws, text in plntxt.items():
                text = ' '.join(text)
                el = r[prev]
                if _ws > prev:
                    el.text += ' '+text
                else: # _ws == prev
                    el.tail = el.tail and el.tail+' '+text or text

            plntxt = {}
        ###
        # continue 27.03ms
        # determine tag attributes
        u, attr = parse_attr(l)
        # continue 34.01ms
        u = split_space(u)
        # continue 36.84ms
        _tag, _id, _class = parse_tag2(u[0])
        # continue 49.54ms
        #
        if ws > prev:
            e_root = r[prev]
        if ws == prev:
            e_root = r[prev].getparent()
        if ws < prev:
            e_root = r[ws].getparent()

            for _ws in r.keys():
                if _ws > ws:
                    r.pop(_ws)
        # continue 68.10ms
        e = SubElement(e_root, _tag or 'div')
        # continue 102.65ms
        e.text = u[1][1:]
        # continue 120.50ms
        if _id:
            e.attrib['id'] = _id

        if _class:
            e.attrib['class'] = _class

        if attr:
            for x in attr[1:-1].split(','):
                k, tmp, v = x.partition('=')
                e.attrib[k.strip()] = v.strip()
        # continue 123.57ms
        r[ws] = e
        prev = ws
        # continue 132.72ms
    return r['']


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


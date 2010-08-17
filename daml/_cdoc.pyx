# -*- coding: utf-8 -*-
cdef object Element, SubElement
from lxml.etree import Element, SubElement
from _cext cimport parse_ws2, parse_attr, split_space, split_pound, split_period, parse_tag, parse_tag2, parse_tag, not_directive, parse_attr2


def parse_ws(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c != u' ':
            return s[:i], s[i:].rstrip()
    return u'', s.rstrip()

def sub_str(unicode a, unicode b):
    cdef Py_ssize_t i
    i = len(b)
    if i == 0:
        return a
    return a[:-i]

def _doc_parse(f):
    cdef unicode ws, _ws, l, _tag, _id, _class
    cdef object e, e_root

    r = {u'': Element(u'html')}
    plntxt = {}

    prev = u''

    for line in f[1:]:
        ws, l = parse_ws2(line)

        ### plntxt queue
        if not_directive(l[0]):
            if ws in plntxt:
                plntxt[ws].append(l)
            else:
                plntxt[ws] = [l]
            continue

        if plntxt:
            for _ws, text in plntxt.items():
                text = u' '.join(text)
                el = r[prev]
                if _ws > prev:
                    el.text += ' '+text
                else: # _ws == prev
                    el.tail = el.tail and el.tail+' '+text or text

            plntxt = {}
        ###


        #u, attr = parse_attr(l)
        u, attr = parse_attr2(l)
        
        u = split_space(u)

        _tag, _id, _class = parse_tag(u[0])

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

        e = SubElement(e_root, _tag or u'div')

        e.text = u[1][1:]

        if _id:
            e.attrib[u'id'] = _id

        if _class:
            e.attrib[u'class'] = _class
        '''
        if attr:
            for x in attr[1:-1].split(u','):
                k, tmp, v = x.partition(u'=')
                e.attrib[k.strip()] = v.strip()
        '''
        if attr is not None:
            e.attrib.update(attr)
        # continue 123.57ms
        r[ws] = e
        prev = ws
        # continue 132.72ms
    return r[u'']

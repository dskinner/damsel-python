# -*- coding: utf-8 -*-
cdef object Element, SubElement
from lxml.etree import Element, SubElement

def parse_ws(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c != u' ':
            return s[:i], s[i:].rstrip()
    return u'', s.rstrip()

cdef tuple parse_ws2(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c != u' ':
            return s[:i], s[i:].rstrip()
    return u'', s.rstrip()

cdef tuple parse_attr(unicode s):
    cdef Py_ssize_t i
    cdef Py_ssize_t j = 0
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c == u' ' and j == 0:
            return s[:i]+s[i:], u''
        elif c == u'(':
            j = i
        elif c == u')':
            i += 1
            return s[:j]+s[i:], s[j:i]
    return s, u''

cdef tuple split_space(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c == u' ':
            return s[:i], s[i:]
    return s, u''

cdef tuple split_pound(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c == u'#':
            return s[:i], s[i:]
    return s, u''

cdef tuple split_period(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c == u'.':
            return s[:i], s[i:]
    return s, u''

cdef tuple parse_tag2(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c
    cdef unicode r1 = u''
    cdef unicode r2 = u''
    cdef unicode _tag = u''
    cdef unicode _id = u''
    cdef unicode _c1 = u''
    cdef unicode _c2 = u''


    for i, c in enumerate(s):
        if c == u'#':
            r1 = s[:i]
            r2 = s[i:]
            break
    if not r1:
        r1 = s
    for i, c in enumerate(r1):
        if c == u'.':
            _tag = r1[:i]
            _c1 = r1[i:]
            break
    if not _tag:
        _tag = r1

    for i, c in enumerate(r2):
        if c == u'.':
            _id = r2[:i]
            _c2 = r2[i:]
            break
    if not _id:
        _id = r2

    return _tag[1:], _id[1:], (_c1+_c2).replace('.', ' ')[1:]

cdef tuple parse_tag(unicode s):
    cdef unicode x

    r = [split_period(x) for x in split_pound(s)]
    return r[0][0][1:], r[1][0][1:], (r[0][1]+r[1][1]).replace(u'.', u' ')[1:]

def sub_str(unicode a, unicode b):
    return a[:-len(b)]


cdef bool not_directive(unicode c):
    cdef Py_UNICODE x = u'%'
    cdef Py_UNICODE y = u'#'
    cdef Py_UNICODE z = u'.'

    if c != x and c != y and c != z:
        return True
    return False


def _doc_parse(f):
    cdef unicode ws, _ws, l, attr, _tag, _id, _class
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
        e = SubElement(e_root, _tag or u'div')
        # continue 102.65ms
        e.text = u[1][1:]
        # continue 120.50ms
        if _id:
            e.attrib[u'id'] = _id

        if _class:
            e.attrib[u'class'] = _class

        if attr:
            for x in attr[1:-1].split(u','):
                k, tmp, v = x.partition(u'=')
                e.attrib[k.strip()] = v.strip()
        # continue 123.57ms
        r[ws] = e
        prev = ws
        # continue 132.72ms
    return r[u'']

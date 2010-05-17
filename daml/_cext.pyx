# -*- coding: utf-8 -*-

def parse_ws(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c != u' ':
            return s[:i], s[i:].rstrip()
    return u'', s.rstrip()

def parse_attr(unicode s):
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

def split_space(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c == u' ':
            return s[:i], s[i:]
    return s, u''

def split_pound(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c == u'#':
            return s[:i], s[i:]
    return s, u''

def split_period(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c == u'.':
            return s[:i], s[i:]
    return s, u''

def parse_tag(unicode s):
    cdef unicode x

    r = [split_period(x) for x in split_pound(s)]
    return r[0][0][1:], r[1][0][1:], (r[0][1]+r[1][1]).replace(u'.', u' ')[1:]

def sub_str(unicode a, unicode b):
    return a[:-len(b)]


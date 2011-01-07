'''
These are python equivalents of the cython parsing extensions, some are hardly
suitable for an actual pure python module of daml.
'''

directives = ['%', '#', '.', '\\']

cdef inline unicode sub_str(unicode a, unicode b):
    cdef Py_ssize_t i = len(b)
    if i == 0:
        return a
    return a[:-i]

cdef inline tuple parse_ws(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c
    
    for i, c in enumerate(s):
        if c != u' ':
            return s[:i], s[i:].rstrip()
    return u'', s.rstrip()


cdef inline tuple split_space(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c == u' ':
            return s[:i], s[i+1:]
    return s, u''

cdef inline tuple split_pound(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c == u'#':
            return s[:i], s[i:]
    return s, u''

cdef inline tuple split_period(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c == u'.':
            return s[:i], s[i:]
    return s, u''

cdef inline tuple parse_tag(unicode s):
    cdef unicode x

    r = [split_period(x) for x in split_pound(s)]
    return r[0][0][1:], r[1][0][1:], (r[0][1]+r[1][1]).replace(u'.', u' ')[1:]

cdef inline tuple parse_attr(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    mark_start = None
    mark_end = None

    key_start = None
    val_start = None
    literal_start = None

    d = {}

    for i, c in enumerate(s):
        if key_start is not None:
            if val_start is not None:
                if i is val_start+1 and (c is u'"' or c is u"'"):
                    literal_start = i
                elif literal_start is not None and c is s[literal_start]:
                    d[s[key_start+1:val_start]] = s[literal_start+1:i]
                    key_start = None
                    val_start = None
                    literal_start = None
                elif literal_start is None and c is u']':
                    d[s[key_start+1:val_start]] = s[val_start+1:i]
                    key_start = None
                    val_start = None
            elif c is u'=':
                val_start = i
        elif c is u'[':
            key_start = i
            if mark_start is None:
                mark_start = i
        elif c is u' ':
            mark_end = i
            break
    
    if mark_start is None:
        return s, d
    if mark_end is None:
        return s[:mark_start], d
    else:
        return s[:mark_start]+s[mark_end:], d

cdef inline unicode parse_inline(unicode s, int i):
    cdef Py_ssize_t a, b, c
    
    if u':' in s:
        a = s.index(':', i)
    else:
        return u''
    if u'(' in s:
        b = s.index(u'(')
    else:
        return u''
    if u' ' in s[a:b] or a > b: # check a>b for attributes that have :
        try:
            a = s.index(u':', a+1)
            parse_inline(s, a)
        except ValueError:
            return u''

    c = s.index(u')')+1
    return s[a+1:c]

cdef inline bint is_assign(unicode s):
    '''
    Tests a python string to determine if it is a variable assignment
    a = 1 # returns True
    map(a, b) # returns False
    '''
    cdef Py_ssize_t a, b
    
    a = s.find('(')
    b = s.find('=')
    if b != -1 and (b < a or a == -1):
        return True
    else:
        return False

cdef inline bint is_directive(unicode c):
    cdef Py_UNICODE w = u'\\'
    cdef Py_UNICODE x = u'%'
    cdef Py_UNICODE y = u'#'
    cdef Py_UNICODE z = u'.'

    if c != w and c != x and c != y and c != z:
        return False
    return True

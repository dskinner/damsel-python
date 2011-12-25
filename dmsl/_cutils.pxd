cdef inline tuple _parse_attr(unicode s):
    cdef Py_ssize_t i, mark_start, mark_end, key_start, val_start, literal_start
    cdef Py_UNICODE c

    mark_start = -1
    mark_end = -1

    key_start = -1
    val_start = -1
    literal_start = -1

    #cdef dict d = {}
    cdef list l = []

    for i, c in enumerate(s):
        if key_start != -1:
            if val_start != -1:
                if i is val_start+1 and (c is u'"' or c is u"'"):
                    literal_start = i
                elif literal_start != -1 and c is s[literal_start]:
                    #d[s[key_start+1:val_start]] = s[literal_start+1:i]
                    l.append((s[key_start+1:val_start], s[literal_start+1:i]))
                    key_start = -1
                    val_start = -1
                    literal_start = -1
                elif literal_start == -1 and c is u']':
                    #d[s[key_start+1:val_start]] = s[val_start+1:i]
                    l.append((s[key_start+1:val_start], s[val_start+1:i]))
                    key_start = -1
                    val_start = -1
            elif c is u'=':
                val_start = i
        elif c is u'[':
            key_start = i
            if mark_start == -1:
                mark_start = i
        elif c is u' ':
            mark_end = i
            break
    
    if mark_start == -1:
        return s, l
    if mark_end == -1:
        return s[:mark_start], l
    else:
        return s[:mark_start]+s[mark_end:], l

cdef inline tuple _parse_tag(unicode s):
    cdef unicode x

    r = [_split_period(x) for x in _split_pound(s)]
    return r[0][0][1:], r[1][0][1:], (r[0][1]+r[1][1]).replace(u'.', u' ')[1:]

cdef inline tuple _parse_ws(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c
    
    for i, c in enumerate(s):
        if c != u' ' and c != u'\t':
            return s[:i], s[i:].rstrip()
    return u'', s.rstrip()

cdef inline tuple _split_space(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c == u' ':
            return s[:i], s[i+1:]
    return s, u''

cdef inline tuple _split_pound(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c == u'#':
            return s[:i], s[i:]
    return s, u''

cdef inline tuple _split_period(unicode s):
    cdef Py_ssize_t i
    cdef Py_UNICODE c

    for i, c in enumerate(s):
        if c == u'.':
            return s[:i], s[i:]
    return s, u''


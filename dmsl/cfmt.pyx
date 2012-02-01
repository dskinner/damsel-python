# -*- coding: utf-8 -*-

cdef inline tuple _parse_format(char* s, tuple args, dict kwargs):
    cdef Py_ssize_t i, inc, key_start, key_end, offset, esc
    cdef bytes e
    cdef bytes result
    cdef bytes new_s = s
    cdef char c
    cdef object obj

    cdef list _args = list(args)
    cdef list traverse
    cdef list keys = []

    key_start = -1
    key_end = -1
    inc = len(args) #increment arg count
    offset = 0
    print '!!!', 'start'
    for i, c in enumerate(s):
        if c is '{':
            if key_start == -1:
                key_start = i
            else:
                key_start = -1
        elif key_start != -1:
            if c is '}' or c is ':':
                key_end = i
            elif c is '!':
                key_end = i+2

            if key_end != -1:
                keys.append(s[key_start+1:key_end])
                new_s = new_s[:key_start+1+offset] + str(inc) + new_s[key_end+offset:]
                offset -= key_end-key_start-2
                inc += 1
                key_start = -1
                key_end = -1

    for e in keys:
        print '@@@', e
        if e[-2:] == '!s':
            esc = False
            e = e[:-2]
        elif e[-2:] == '!r':
            esc = True
            e = e[:-2]
        else:
            esc = True

        if e.isdigit():
            i = int(e)
            obj = args[i]
        elif '[' in e:
            traverse = [x.replace(']', '') for x in e.split('[')]
            obj = kwargs[traverse[0]]
            for x in traverse[1:]:
                obj = obj[x]
        elif '.' in e:
            print e
            traverse = [x for x in e.split('.')]
            obj = kwargs[traverse[0]]
            for x in traverse[1:]:
                obj = getattr(obj, x)
        else:
            obj = kwargs[e]

        if isinstance(obj, (float, int)):
            _args.append(obj)
        elif esc:
            result = repr(obj).replace('<', '&lt;').replace('>', '&gt;')
            if isinstance(obj, str):
                result = result[1:-1]
            elif isinstance(obj, unicode):
                result = result[2:-1]
            _args.append(result)
        else:
            _args.append(obj)

    return (new_s, _args)

def fmt(__fmt_string__, *args, **kwargs):
    __fmt_string__, _args = _parse_format(__fmt_string__, args, kwargs)
    return __fmt_string__.format(*_args)



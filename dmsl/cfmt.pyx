# -*- coding: utf-8 -*-

cdef inline tuple _parse_format(char* s, list args, dict kwargs):
    cdef Py_ssize_t i, key_start, conversion_start, offset
    cdef str e
    cdef str result
    cdef bytes new_s = s
    cdef char c

    cdef list escape = []
    cdef list cnv_idx = []

    key_start = -1
    conversion_start = -1

    for i, c in enumerate(s):
        if key_start != -1:
            if c is '}' or c is ':':
                escape.append(s[key_start+1:i])
                key_start = -1
                conversion_start = -1
            elif c is '!':
                conversion_start = i
            elif conversion_start != -1:
                if c is 'r':
                    escape.append(s[key_start+1:conversion_start])
                    cnv_idx.append(conversion_start)
                conversion_start = -1
                key_start = -1

        if c is '{':
            key_start = i

    for e in escape:
        if e.isdigit():
            i = int(e)
            if isinstance(args[i], (float, int)):
                continue
            else:
                result = repr(args[i]).replace('<', '&lt;').replace('>', '&gt;')
                if isinstance(args[i], str):
                    result = result[1:-1]
                if isinstance(args[i], unicode): # TODO this might need checks for PY3
                    result = result[2:-1]
                args[i] = result
        else:
            # factor 3 str(), factor 3 replace().replace()
            if isinstance(kwargs[e], (float, int)):
                continue
            else:
                result = repr(kwargs[e]).replace('<', '&lt;').replace('>', '&gt;')
                if isinstance(kwargs[e], str):
                    result = result[1:-1]
                elif isinstance(kwargs[e], unicode):
                    result = result[2:-1]
                kwargs[e] = result

    offset = 0
    for i in cnv_idx:
        new_s = s[:i+offset] + s[i+offset+2:]
        i -= 2
    return (new_s, args, kwargs)

def fmt(__fmt_string__, *args, **kwargs):
    # factor 2 list(args)
    # TODO _parse_format messing up apks in apk bot, nested dict (SON)
    #__fmt_string__, args, kwargs = _parse_format(__fmt_string__, list(args), kwargs)
    
    return __fmt_string__.format(*args, **kwargs)



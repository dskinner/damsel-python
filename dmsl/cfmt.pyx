# -*- coding: utf-8 -*-

cdef inline tuple _parse_format(char* s, list args, dict kwargs):
    cdef Py_ssize_t i, key_start, conversion_start
    cdef str e
    cdef char c

    cdef list escape = []

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
                args[i] = str(args[i].replace('<', '&lt;').replace('>', '&gt;'))
        else:
            # factor 3 str(), factor 3 replace().replace()
            if isinstance(kwargs[e], (float, int)):
                continue
            else:
                kwargs[e] = str(kwargs[e]).replace('<', '&lt;').replace('>', '&gt;')

    return (args, kwargs)

def fmt(__fmt_string__, *args, **kwargs):
    # factor 2 list(args)
    args, kwargs = _parse_format(__fmt_string__, list(args), kwargs)
    return __fmt_string__.format(*args, **kwargs)



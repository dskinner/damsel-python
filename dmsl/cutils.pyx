from _cutils cimport _parse_attr, _parse_ws, _split_space

def parse_attr(unicode s):
    return _parse_attr(s)

def parse_ws(unicode s):
    return _parse_ws(s)

def split_space(unicode s):
    return _split_space(s)

def sub_str(unicode a, unicode b):
    cdef Py_ssize_t i = len(b)
    if i == 0:
        return a
    return a[:-i]

def sub_strs(*args):
    r = args[0]
    for x in range(1, len(args)):
        i = len(args[x])
        if i == 0:
            continue
        r = r[:-i]
    return r

def parse_inline(unicode s, int i):
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

def var_assign(unicode s):
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
    return False


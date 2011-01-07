'''
These are python equivalents of the cython parsing extensions, some are hardly
suitable for an actual pure python module of daml.
'''

directives = ['%', '#', '.', '\\']

def sub_str(a, b):
    i = len(b)
    if i == 0:
        return a
    return a[:-i]

def parse_ws(s):
    for i, c in enumerate(s):
        if c != u' ':
            return s[:i], s[i:].rstrip()
    return u'', s.rstrip()

def split_space(s):
    for i, c in enumerate(s):
        if c == u' ':
            return s[:i], s[i+1:]
    return s, u''

def split_pound(s):
    for i, c in enumerate(s):
        if c == u'#':
            return s[:i], s[i:]
    return s, u''

def split_period(s):
    for i, c in enumerate(s):
        if c == u'.':
            return s[:i], s[i:]
    return s, u''

def parse_tag(s):
    '''
    accepts input such as
    %tag.class#id.one.two
    and returns
    ('tag', 'id', 'class one two')
    '''
    r = [split_period(x) for x in split_pound(s)]
    return r[0][0][1:], r[1][0][1:], (r[0][1]+r[1][1]).replace(u'.', u' ')[1:]

def parse_attr(s):
    mark_start = None
    mark_end = None

    key_start = None
    val_start = None
    literal_start = None

    d = {}

    for i, c in enumerate(s):
        if key_start is not None:
            if val_start is not None:
                if i == val_start+1 and (c == u'"' or c == u"'"):
                    literal_start = i
                elif literal_start is not None and c == s[literal_start]:
                    d[s[key_start+1:val_start]] = s[literal_start+1:i]
                    key_start = None
                    val_start = None
                    literal_start = None
                elif literal_start is None and c == u']':
                    d[s[key_start+1:val_start]] = s[val_start+1:i]
                    key_start = None
                    val_start = None
            elif c == u'=':
                val_start = i
        elif c == u'[':
            key_start = i
            if mark_start is None:
                mark_start = i
        elif c == u' ':
            mark_end = i
            break
    
    if mark_start is None:
        return s, d
    if mark_end is None:
        return s[:mark_start], d
    else:
        return s[:mark_start]+s[mark_end:], d

def parse_inline(s, i):
    if u':' in s:
        a = s.index(u':', i)
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

def is_assign(s):
    '''
    Tests a python string to determine if it is a variable assignment
    a = 1 # returns True
    map(a, b) # returns False
    '''
    a = s.find('(')
    b = s.find('=')
    if b != -1 and (b < a or a == -1):
        return True
    else:
        return False

def is_directive(c):
    x = u'%'
    y = u'#'
    z = u'.'

    if c != x and c != y and c != z:
        return False
    return True

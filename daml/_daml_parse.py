directives = ['%', '#', '.']

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

def parse_inline(s, i=None):
    if i is not None:
        a = s.index(':', i)
    elif ':' in s:
        a = s.index(':')
    else:
        return None
    if '(' in s:
        b = s.index('(')
    else:
        return None
    if ' ' in s[a:b] or a > b: # check a>b for attributes that have :
        try:
            a = s.index(':', a+1)
            parse_inline(s, a)
        except ValueError:
            return None

    c = s.index(')')+1
    return s[a+1:c]

def parse_inlines(s):
    if ':' not in s:
        return s, ()
    
    l = []
    inline = parse_inline(s)
    i = 0
    while inline is not None:
        s = s.replace(':'+inline, '{'+str(i)+'}')
        l.append(inline)
        inline = parse_inline(s)
        i += 1
    return s, l

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

def expand_line(ws, l, i, f):
    el, attr = parse_attr(l)
    tag, txt = split_space(el)
    
    # Check for inlined tag hashes
    if txt != u'' and (txt[0] in directives or txt[-1] == ':'):
        l = l.replace(txt, u'')
        f.pop(i)
        f.insert(i, ws+l)
        f.insert(i+1, ws+u' '+txt)
    return l

def _pre_parse(_f):
    f = _f[:]
    
    py_queue = []
    py_count = 0
    
    mixed_ws = None
    mixed_ws_last = None
    get_new_ws = False
    
    i = 0
    
    while i < len(f):
        ws, l = parse_ws(f[i])
        
        if not l:
            f.pop(i)
            continue
        
        if l[0] in directives:
            l = expand_line(ws, l, i, f)
        # else if list comprehension
        elif (l[0] == '[' and l[-1] == ']'):
            py_queue.append('globals()["__py_parse__"].append('+l+')')
            f.pop(i)
            f.insert(i, ws+'{{{0}}}'.format(py_count))
            py_count += 1
            i += 1
            continue
        # else if not a filter or mixed content
        elif l[0] != ':' and l[-1] != ':':
            if is_assign(l):
                py_queue.append(l)
                f.pop(i)
            else:
                py_queue.append('globals()["__py_parse__"].append('+l+')')
                f.pop(i)
                f.insert(i, ws+'{{{0}}}'.format(py_count))
                py_count += 1
                i += 1
            continue
        
        # check for continued lines
        while l[-1] == '\\':
            _ws, _l = parse_ws(f.pop(i+1))
            l = l[:-1] + _l
            
        
        # inspect for format variables
        if '{' in l: # and mixed is None:
            l, inlines = parse_inlines(l)
            py_queue.append(u'globals()["__py_parse__"].append(fmt.format("""{0}""", {1}))'.format(l, ','.join(inlines)))
            f.pop(i)
            f.insert(i, ws+u'{{{0}}}'.format(py_count))
            py_count += 1
            i += 1
            continue
        
        # handle filter
        if l[0] == ':':
            filter = l[1:].partition(' ')
            
            func = filter[2]
            is_block = (filter[0] == 'block')
            
            filter = [filter[0]+'("""'+filter[2]]
            j = i+1
            fl_ws = None # first-line whitespace
            while j < len(f):
                _ws, _l = parse_ws(f[j])
                if _ws <= ws:
                    break
                fl_ws = fl_ws or _ws
                f.pop(j)
                filter.append(sub_str(_ws, fl_ws)+_l)
            filter.append('""")')
            f.pop(i)
            if is_block:
                f.insert(i, ws+'{{block}}{{{0}}}'.format(func))
            else:
                f.insert(i, ws+'{{{0}}}'.format(py_count))
                py_count += 1
            py_queue.append('globals()["__py_parse__"].append('+'\n'.join(filter)+')')
        
        # handle mixed content
        elif l[-1] == ':':
            mixed_ws = mixed_ws_last = ws
            get_new_ws = True
            py_queue.append(u'__mixed_content__ = []')
            py_queue.append(l)
            f.pop(i)
            j = i
            mixed_closed = False
            while j < len(f):
                _ws, _l = parse_ws(f[j])
                if not _l:
                    f.pop(j)
                    continue
                
                if _ws <= mixed_ws and _l[:4] not in ['else', 'elif']:
                    py_queue.append(u'globals()["__py_parse__"].append(list(__mixed_content__))')
                    f.insert(j, mixed_ws+u'{{{0}}}'.format(py_count))
                    py_count += 1
                    i = j
                    mixed_closed = True
                    break
                elif _l[0] in directives:
                    _l = expand_line(_ws, _l, j, f)
                    if get_new_ws or sub_str(_ws, mixed_ws) <= mixed_ws_last:
                        mixed_ws_last = sub_str(_ws, mixed_ws)
                        get_new_ws = False
                    _l, inlines = parse_inlines(_l)
                    py_queue.append(mixed_ws_last+u'__mixed_content__.append(fmt.format("""{0}{1}""", {2}))'.format(sub_str(sub_str(_ws, mixed_ws_last), mixed_ws), _l, ','.join(inlines)))
                    f.pop(j)
                    continue
                # is this a list comprehension?
                elif _l[0] == '[' and _l[-1] == ']':
                    py_queue.append(mixed_ws_last+u'__mixed_content__.extend({0})'.format(_l))
                    f.pop(j)
                else:
                    if _l[-1] == ':':
                        get_new_ws = True
                    py_queue.append(sub_str(_ws, mixed_ws)+_l)
                    f.pop(j)
                    continue
            # maybe this could be cleaner? instead of copy and paste
            if not mixed_closed:
                py_queue.append(u'globals()["__py_parse__"].append(list(__mixed_content__))')
                f.insert(j, mixed_ws+u'{{{0}}}'.format(py_count))
                py_count += 1
                i = j
        # handle standalone embedded function calls
        elif ':' in l:
            l, inlines = parse_inlines(l)
            if len(inlines) != 0:
                py_queue.append(u'globals()["__py_parse__"].append(fmt.format("""{0}""", {1}))'.format(l, ','.join(inlines)))
                f.pop(i)
                f.insert(i, ws+u'{{{0}}}'.format(py_count))
                py_count += 1
                i += 1
                continue
        
        i += 1
    
    return f, py_queue

def css(s):
    s = s.splitlines()
    n = s[0]
    s = s[1:]
    return ['%link[rel=stylesheet][href={0}{1}]'.format(n, x) for x in s]

def block(s):
    s = s.splitlines()
    n = s[0]
    s = s[1:]
    f, q = _pre_parse(s)
    s = _py_parse(f, q, sandbox)
    sandbox['__blocks__'][n] = s
    return u''

def _py_parse(_f, py_queue, sandbox):
    f = _f[:]
    
    py_str = '\n'.join(py_queue)
    if py_str == '':
        return f
    try:
        cc = compile('globals()["__py_parse__"] = []\nfmt.namespace=globals()\n'+py_str, '<string>', 'exec')
        eval(cc, sandbox)
    except Exception as e:
        print '=================='
        print 'Compilation String'
        print '=================='
        print py_str
        print '------------------'
        raise e
    
    i = 0
    py_count = 0
    while i < len(f):
        t = '{%s}' % py_count
        if t in f[i]:
            # these should always be blank lines... i think...
            
            #
            o = sandbox['__py_parse__'][py_count]
            if isinstance(o, (list, tuple)):
                ws = f.pop(i).replace(t, '')
                for x in o:
                    f.insert(i, ws+x)
                    i += 1
                py_count += 1
                continue
            else:
                f[i] = f[i].replace(t, o)
                i += 1
                py_count += 1
                continue
        elif '{block}' in f[i]:
            tmp = f[i]
            tmp = tmp.replace('{block}', '')
            name = tmp[tmp.index('{')+1:tmp.index('}')]
            if name in sandbox['__blocks__']:
                ws = f.pop(i).replace('{block}{'+name+'}', '')
                for x in sandbox['__blocks__'][name]:
                    f.insert(i, ws+x)
                    i += 1
                del sandbox['__blocks__'][name]
                continue
            else:
                f.pop(i)
                continue
        i += 1
    
    return f

if __name__ == '__main__':
    import sys
    import codecs
    from time import time
    
    _f = codecs.open(sys.argv[1], 'r', encoding='utf-8').read().splitlines()
    import _sandbox

    sandbox = _sandbox.new()
    sandbox.update({'css': css, 'block': block})
    
    try:
        sys.argv[2]
        times = []
        for x in range(1000):
            a = time()
            r, q = _pre_parse(_f)
            _py_parse(r, q, sandbox)
            times.append(time()-a)
        for x in range(times.count(0.0)):
            times.remove(0.0)
        print min(times), times[0]
    except Exception as e:
        result, q = _pre_parse(_f)
        py = _py_parse(result, q, sandbox)
        
        print '\n=== Original ===\n'
        for l in _f:
            print `l`
        print '\n=== PreParse ===\n'
        for line in result:
            print `line`
        print '\n=== PyQueue ===\n'
        for line in q:
            print `line`
        print '\n=== PyParse ===\n'
        for line in py:
            print `line`


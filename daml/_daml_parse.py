import _sandbox

sandbox = _sandbox.new()
def css(s):
    s = s.splitlines()
    n = s[0]
    s = s[1:]
    return ['%link[rel=stylesheet][href={0}{1}]'.format(n, x) for x in s]
sandbox.update({'css': css})

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

def parse_inline(s):
    if ':' in s:
        a = s.index(':')
    else:
        return None
    if '(' in s:
        b = s.index('(')
    else:
        return None
    if ' ' in s[a:b] or a > b: # check a>b for attributes that have :
        return None

    c = s.index(')')+1
    return s[a+1:c]


def _pre_parse(_f):
    f = _f[:]
    
    i = 0
    
    py_queue = []
    py_count = 0
    mixed = None
    mixed_ws = None
    mixed_ws_last = None
    get_new_ws = False
    filter = None
    filter_ws = None
    
    while i < len(f):
        ws, l = parse_ws(f[i])
        if not l:
            f.pop(i)
            continue
        
        if l[0] in directives:
            el, attr = parse_attr(l)
            tag, txt = split_space(el)
            
            # Check for inlined tag hashes
            if txt != u'' and (txt[0] in directives or txt[-1] == ':'):
                l = l.replace(txt, u'')
                f.pop(i)
                f.insert(i, ws+l)
                f.insert(i+1, ws+u' '+txt)
        # check for single-line python call
        # TODO handle list comprehensions
        elif l[:3] not in ['if ', 'for', 'whi'] and mixed is None and l[0] != ':':
            py_queue.append(ws+l)
            f.pop(i)
            continue
        
        # inspect for format variables
        if '{' in l and mixed is None:
            py_queue.append(u'globals()["__py_parse__"].append(fmt.format("""{0}"""))'.format(l))
            f.pop(i)
            f.insert(i, ws+u'{{{0}}}'.format(py_count))
            py_count += 1
            i += 1
            continue
        
        # handle mixed content
        if mixed is not None:
            if ws <= mixed_ws and l[:4] not in ['else', 'elif']:
                py_queue.append(u'globals()["__py_parse__"].append(list(__mixed_content__))')
                f.insert(i, mixed_ws+u'{{{0}}}'.format(py_count))
                py_count += 1
                mixed = None
                i += 1
                continue
            elif l[0] in directives:
                ### parse inline python, ie, %p something, :greet('Daniel')
                inlines = []
                inline = parse_inline(l)
                z = 0
                while inline is not None:
                    l = l.replace(':'+inline, '{'+str(z)+'}')
                    inlines.append(inline)
                    inline = parse_inline(l)
                    z += 1
                ###
                if get_new_ws or sub_str(ws, mixed_ws) <= mixed_ws_last:
                    mixed_ws_last = sub_str(ws, mixed_ws)
                    get_new_ws = False
                
                py_queue.append(mixed_ws_last+u'__mixed_content__.append(fmt.format("""{0}{1}""", {2}))'.format(sub_str(sub_str(ws, mixed_ws_last), mixed_ws), l, ','.join(inlines)))
                f.pop(i)
                continue
            else:
                if l[:3] in ['if ', 'for', 'whi']:
                    get_new_ws = True
                py_queue.append(sub_str(ws, mixed_ws)+l)
                f.pop(i)
                continue
        
        # handle filter
        if l[0] == ':':
            filter = l[1:].partition(' ')
            filter = [filter[0]+'("""'+filter[2]]
            j = i+1
            fl_ws = None
            while True:
                _ws, _l = parse_ws(f[j])
                if _ws <= ws:
                    break
                if fl_ws is None:
                    fl_ws = _ws
                f.pop(j)
                filter.append(sub_str(_ws, fl_ws)+_l)
            filter.append('""")')
            f.pop(i)
            f.insert(i, ws+'{{{0}}}'.format(py_count))
            py_queue.append('globals()["__py_parse__"].append('+'\n'.join(filter)+')')
            py_count += 1
        
        # inspect for mixed content
        if mixed is None and l[-1] == ':':
            mixed = True
            mixed_ws = mixed_ws_last = ws
            get_new_ws = True
            py_queue.append(u'__mixed_content__ = []')
            py_queue.append(l)
            f.pop(i)
            continue
        
        i += 1
    
    return f, py_queue

def _py_parse(f, py_queue):
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
    
    #return '\n'.join(f).format(*sandbox['__py_parse__'])
    i = 0
    py_count = 0
    while i < len(f):
        t = '{%s}' % py_count
        if t in f[i]:
            o = sandbox['__py_parse__'][py_count]
            if isinstance(o, list):
                f[i] = f[i].replace(t, '')
                for x in o:
                    f.insert(i, f[i]+x)
                    #f.insert(i, x)
                    i += 1
            else:
                f[i] = f[i].replace(t, o)
            py_count += 1
        i += 1
    
    return '\n'.join(f)
    
    
'''
def _pre_parse(f):
    f = f[:] # this fixes errors for benchmarks with multiple iterative runs
    
    py_queue = []
    py_count = 0
    offset = 0
    
    mixed_content = None
    mixex_content_ws = None
    filter = None
    filter_ws = None
    
    for i, line in enumerate(f[:]):
        ws, l = parse_ws(line)
        
        if not l:
            f.pop(i+offset)
            offset -= 1
            continue
        
        # TODO handle use-cases:
        # %li %a[href=/] A Link
        # %ul for x in l:
        while True:
            if l[0] in directives:
                el, attr = parse_attr(l)
                tag, txt = split_space(el)
                if txt != u'' and (txt[0] in directives or txt[-1] == ':'): # TODO check for escaped colons
                    f.pop(i+offset)
                    f.insert(i+offset, ws+l.replace(txt, u''))
                    offset += 1
                    ws += u' '
                    f.insert(i+offset, ws+txt)
                    l = txt
                else:
                    break
            else:
                break
        
        if l[0] not in directives and l[:3] not in ['if ', 'for', 'whi'] and \
            mixed_content is None:
            py_queue.append(ws+l)
            f.pop(i+offset)
            f.insert(i+offset, ws+u'{{{0}}}'.format(py_count))
            py_count += 1
            continue
        
        if '{' in l and mixed_content is None:
            py_queue.append(u'fmt.format({0})'.format(l))
            f.pop(i+offset)
            f.insert(i+offset, ws+u'{{{0}}}'.format(py_count))
            py_count += 1
            continue
        
        # TODO handle filter
        
        # TODO handle mixed-content
        if mixed_content is not None:
            if ws <= mixed_content_ws and l[:4] not in ['else', 'elif']:
                py_queue.append(u'list(__mixed_content__)')
                f.insert(i+offset, mixed_content_ws+u'{{{0}}}'.format(py_count))
                py_count += 1
                mixed_content = None
            elif l[0] in directives:
                ### parse inline python
                inlines = []
                inline = parse_inline(l)
                z = 0
                while inline is not None:
                    l = l.replace(':'+inline, '{'+str(z)+'}')
                    inlines.append(inline)
                    inline = parse_inline(l)
                    z += 1
                ###
                py_queue.append(sub_str(ws, mixed_content_ws)+u'__mixed_content__.append(fmt.format("""{0}{1}""", {2}))'.format(ws, l, ','.join(inlines)))
                f.pop(i+offset)
                offset -= 1
            else:
                py_queue.append(sub_str(ws, mixed_content_ws)+l)
                f.pop(i+offset)
                offset -= 1
        
        # TODO inspect for filter
        
        # TODO inspect for mixed-content
        if mixed_content is None and l[-1] == ':':
            mixed_content = True
            mixed_content_ws = ws
            py_queue.append(u'__mixed_content__ = []')
            py_queue.append(l)
            f.pop(i+offset)
            offset -= 1
    
    return f, py_queue
'''

if __name__ == '__main__':
    import sys
    import codecs
    from time import time
    
    _f = codecs.open(sys.argv[1], 'r', encoding='utf-8').read().splitlines()
    
    try:
        sys.argv[2]
        times = []
        for x in range(1000):
            a = time()
            r, q = _pre_parse(_f)
            _py_parse(r, q)
            times.append(time()-a)
        for x in range(times.count(0.0)):
            times.remove(0.0)
        print min(times), times[0]
    except Exception as e:
        result, q = _pre_parse(_f)
        py = _py_parse(result, q)
        
        for line in result:
            print `line`
        print '\n---\n'
        for line in q:
            print `line`
        
        print py


directives = ['%', '#', '.']

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

def _pre_parse(f):
    f = f[:] # this fixes errors for benchmarks with multiple iterative runs
    
    py_queue = []
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
        
        
        # TODO handle filter
        
        # TODO handle mixed-content
        if mixed_content is not None:
            if ws <= mixed_content_ws and l[:4] not in ['else', 'elif']:
                py_queue.append(mixed_content_ws+'list(__mixed_content__)')
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
                py_queue.append(ws+'__mixed_content__.append(fmt.format("""{0}{1}""", {2}))'.format(ws, l, ','.join(inlines)))
            else:
                py_queue.append(ws+l)
                f.pop(i+offset)
                offset -= 1
        
        # TODO inspect for filter
        
        # TODO inspect for mixed-content
        if mixed_content is None and l[-1] == ':':
            mixed_content = True
            mixed_content_ws = ws
            py_queue.append(ws+'__mixed_content__ = []')
            py_queue.append(ws+l)
            f.pop(i+offset)
            offset -= 1
    
    return f, py_queue

if __name__ == '__main__':
    import sys
    import codecs
    
    _f = codecs.open(sys.argv[1], 'r', encoding='utf-8').read().splitlines()
    result, q = _pre_parse(_f)
    
    for line in result:
        print `line`
    print '\n---\n'
    for line in q:
        print `line`


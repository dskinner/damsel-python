from cutils import parse_attr, split_space, parse_inline, parse_ws, sub_str, sub_strs, var_assign
from _sandbox import _open

directives = ['%', '#', '.', '\\']

def parse_inlines(s):
    if u':' not in s:
        return s, ''
    
    l = []
    inline = parse_inline(s, 0)
    i = 0
    while inline != u'':
        s = s.replace(u':'+inline, u'{'+str(i)+u'}')
        l.append(inline)
        inline = parse_inline(s, 0)
        i += 1
    l = u','.join(l)
    if l != u'':
        l += u','
    return s, l

def expand_line(ws, l, i, f):
    el, attr = parse_attr(l)
    tag, txt = split_space(el)
    
    # Check for inlined tag hashes
    if txt != u'' and (txt[0] in directives or txt[-1] == u':' or (txt[0] == u'[' and txt[-1] == u']')):
        l = l.replace(txt, u'')
        f[i] = ws+l
        f.insert(i+1, ws+u' '+txt)
    return l

txt_cmd = u'__py_parse__["{0}_{1}"] = {2}'
txt_fmt = u'__py_parse__["{0}_{1}"] = fmt(u"""{2}""", {3}**locals())'

def add_strs(*args):
    s = ''
    for arg in args:
        s += arg
    return s

def _pre(_f):
    f = _f[:]
    
    py_queue = []
    py_id = id(py_queue)
    py_count = 0
    
    mixed_ws = None
    mixed_ws_last = None
    get_new_mixed_ws = False
    
    comment = None
    
    i = 0
    
    while i < len(f):
        ws, l = parse_ws(f[i])
        if not l:
            del f[i]
            continue
        
        ### check for comments
        if l[:3] in [u'"""', u"'''"]:
            if comment is None:
                comment = l[:3]
                del f[i]
                continue
            elif l[:3] == comment:
                comment = None
                del f[i]
                continue
        
        if comment is not None:
            del f[i]
            continue
        ###
        
        ### maybe something better?
        if l[:8] == u'extends(':
            del f[i]
            _f = _open(l.split("'")[1]).readlines()
            for j, x in enumerate(_f):
                f.insert(i+j, x)
            continue
        if l[:8] == u'include(':
            del f[i]
            _f = _open(l.split("'")[1]).readlines()
            for j, x in enumerate(_f):
                f.insert(i+j, ws+x)
            continue
        ###
        
        # check for continued lines
        if l[-1] == u'\\':
            while l[-1] == u'\\':
                _ws, _l = parse_ws(f.pop(i+1))
                l = l[:-1] + _l
            f[i] = ws+l
        
        if l[0] in directives:
            l = expand_line(ws, l, i, f)
        elif l[0] == u'[' and l[-1] == u']': # else if list comprehension
            py_queue.append(txt_cmd.format(py_id, py_count, l))
            f[i] = ws+u'{{{0}}}'.format(py_count)
            py_count += 1
            i += 1
            continue
        # handle raise
        elif l[:5] == u'raise':
            py_queue.append(l)
            del f[i]
            i += 1
            continue
        # else if not a filter or mixed content
        elif l[0] != u':' and l[-1] != u':':
            if var_assign(l):
                py_queue.append(l)
                del f[i]
            else:
                py_queue.append(txt_cmd.format(py_id, py_count, l))
                f[i] = ws+u'{{{0}}}'.format(py_count)
                py_count += 1
                i += 1
            continue
        
        # inspect for format variables
        # and l[:3] is to prevent triggering dicts as formats in for, if, while statements
        if u'{' in l and l[:3] not in ['for', 'if ', 'whi']: # and mixed is None:
            l, inlines = parse_inlines(l)
            py_queue.append(txt_fmt.format(py_id, py_count, l, inlines))
            f[i] = ws+u'{{{0}}}'.format(py_count)
            py_count += 1
            i += 1
            continue
        
        # handle filter
        if l[0] == u':':
            func, sep, args = l[1:].partition(u' ')
            filter = [func+u'(u"""'+args]
            j = i+1
            fl_ws = None # first-line whitespace
            while j < len(f):
                _ws, _l = parse_ws(f[j])
                if _ws <= ws:
                    break
                fl_ws = fl_ws or _ws
                del f[j]
                filter.append(sub_str(_ws, fl_ws)+_l)
            filter.append(u'""", locals())')
            
            if func == u'block':
                f[i] = ws+u'{{block}}{{{0}}}'.format(args)
                py_queue.append(txt_cmd.format(py_id, py_count, u'\n'.join(filter)))
            else:
                f[i] = ws+u'{{{0}}}'.format(py_count)
                py_queue.append(txt_cmd.format(py_id, py_count, u'\n'.join(filter)))
                py_count += 1
        
        # handle mixed content
        elif l[-1] == u':':
            orig_mixed_ws = ws
            mixed_ws = []
            mixed_ws_offset = []
            mixed_ws_last = ws
            
            content_ws = []
            content_ws_offset = []
            content_ws_last = None
            
            mixed_content_ws_offset = []
            
            get_new_mixed_ws = True
            get_new_content_ws = True
            level = 1
            
            content_ws_offset_append = False
            
            py_queue.append(u'__mixed_content__ = []')
            py_queue.append(l)
            del f[i]
            mixed_closed = False
            while i < len(f):
                _ws, _l = parse_ws(f[i])
                if not _l:
                    del f[i]
                    continue
                
                if content_ws_last is None:
                    content_ws_last = _ws
                
                if _ws <= orig_mixed_ws and _l[:4] not in [u'else', u'elif']:
                    py_queue.append(u'__py_parse__["{0}_{1}"] = list(__mixed_content__)'.format(py_id, py_count))
                    f.insert(i, mixed_ws[0]+u'{{{0}}}'.format(py_count))
                    py_count += 1
                    mixed_closed = True
                    break
                
                # check for ws changes here, python statement ws only
                if get_new_mixed_ws:
                    get_new_mixed_ws = False
                    mixed_ws_offset.append(sub_strs(_ws, mixed_ws_last))
                    if content_ws_offset_append:
                        mixed_content_ws_offset.append(sub_strs(_ws, mixed_ws_last))
                    mixed_ws.append(mixed_ws_last)
                

                # handles catching n[-1] of if,elif,else and related to align correctly
                while mixed_ws and _ws == mixed_ws[-1]:
                    mixed_ws_offset.pop()
                    mixed_ws.pop()
                
                #if _ws == mixed_ws[-1]:
                #    mixed_ws_offset.pop()
                #    mixed_ws.pop()

                # handles catching n[1:-1] of if,elif,else and related to align correctly
                while mixed_ws and _ws <= mixed_ws[-1]:
                    mixed_ws_offset.pop()
                    mixed_ws.pop()
                
                '''
                if get_new_content_ws:
                    get_new_content_ws = False
                    content_ws_offset.append(sub_strs(_ws, content_ws_last))
                    content_ws.append(content_ws_last)
                '''
                
                if _l[0] in directives:
                    _l = expand_line(_ws, _l, i, f)
                    _l, inlines = parse_inlines(_l)
                    
                    '''
                    if _ws > content_ws[-1]:
                        content_ws_offset.append(sub_strs(_ws, content_ws[-1]))
                        content_ws.append(_ws)
                    while _ws < content_ws[-1]:
                        content_ws_offset.pop()
                        content_ws.pop()
                    '''
                    #tmp_ws = add_strs(*content_ws_offset+mixed_content_ws_offset)
                    tmp_ws = sub_strs(_ws, orig_mixed_ws, *mixed_ws_offset)
                    #print '###', _l, mixed_ws_offset
                    py_queue.append(add_strs(*mixed_ws_offset)+u'__mixed_content__.append(fmt("""{0}{1}""", {2}**locals()))'.format(tmp_ws, _l, inlines))
                    
                    del f[i]
                    continue
                # is this a list comprehension?
                elif _l[0] == '[' and _l[-1] == ']':
                    py_queue.append(add_strs(*mixed_ws_offset)+u'__mixed_content__.extend({0})'.format(_l))
                    del f[i]
                else:
                    if _l[-1] == ':':
                        mixed_ws_last = _ws
                        get_new_mixed_ws = True
                        content_ws_offset_append = True
                    
                    py_queue.append(add_strs(*mixed_ws_offset)+_l)
                    
                    del f[i]
                    continue
            # maybe this could be cleaner? instead of copy and paste
            if not mixed_closed:
                py_queue.append(u'__py_parse__["{0}_{1}"] = list(__mixed_content__)'.format(py_id, py_count))
                f.insert(i, mixed_ws[0]+u'{{{0}}}'.format(py_count))
                py_count += 1
        # handle standalone embedded function calls
        elif ':' in l:
            l, inlines = parse_inlines(l)
            if inlines != '':
                py_queue.append(txt_fmt.format(py_id, py_count, l, inlines))
                f[i] = ws+u'{{{0}}}'.format(py_count)
                py_count += 1
                i += 1
                continue
        
        i += 1
    
    return f, py_queue


if __name__ == '__main__':
    import codecs
    import sys
    _f = codecs.open(sys.argv[1], 'r', 'utf-8').read().expandtabs(4).splitlines()
    f, q = _pre(_f)
    print '\n=== F ==='
    for x in f:
        print `x`
    print '\n=== Q ==='
    for x in q:
        print `x`
    

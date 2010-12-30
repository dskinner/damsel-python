from _parse_ext import *
from _sandbox import _open

def parse_inlines(s):
    if ':' not in s:
        return s, ()
    
    l = []
    inline = parse_inline(s, 0)
    i = 0
    while inline != u'':
        s = s.replace(':'+inline, '{'+str(i)+'}')
        l.append(inline)
        inline = parse_inline(s, 0)
        i += 1
    return s, l

def expand_line(ws, l, i, f):
    el, attr = parse_attr(l)
    tag, txt = split_space(el)
    
    # Check for inlined tag hashes
    if txt != u'' and (is_directive(txt[0]) or txt[-1] == u':'):
        l = l.replace(txt, u'')
        f.pop(i)
        f.insert(i, ws+l)
        f.insert(i+1, ws+u' '+txt)
    return l

def _parse_pre(_f):
    f = _f[:]
    
    py_queue = []
    py_id = id(py_queue)
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
        
        ### maybe something better?
        if l[:8] == 'extends(':
            _f = _open(l.split("'")[1]).readlines()
            f.pop(i)
            
            j = i
            for x in _f:
                f.insert(j, x)
                j += 1
            continue
        elif l[:8] == 'include(':
            _f = _open(l.split("'")[1]).readlines()
            f.pop(i)
            
            j = i
            for x in _f:
                f.insert(j, ws+x)
                j += 1
            continue
        ###
        
        if is_directive(l[0]):
            l = expand_line(ws, l, i, f)
        # else if list comprehension
        elif (l[0] == '[' and l[-1] == ']'):
            py_queue.append(u'globals()["__py_parse__"]["{0}_{1}"] = {2}'.format(py_id, py_count, l))
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
                py_queue.append(u'globals()["__py_parse__"]["{0}_{1}"] = {2}'.format(py_id, py_count, l))
                f.pop(i)
                f.insert(i, ws+u'{{{0}}}'.format(py_count))
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
            py_queue.append(u'globals()["__py_parse__"]["{0}_{1}"] = fmt.format("""{2}""", {3})'.format(py_id, py_count, l, u','.join(inlines)))
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
            
            filter = [filter[0]+'(u"""'+filter[2]]
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
                f.insert(i, ws+u'{{block}}{{{0}}}'.format(func))
                py_queue.append(u'globals()["__py_parse__"]["{0}_{1}"] = {2}'.format(py_id, py_count, u'\n'.join(filter)))
            else:
                f.insert(i, ws+u'{{{0}}}'.format(py_count))
                py_queue.append(u'globals()["__py_parse__"]["{0}_{1}"] = {2}'.format(py_id, py_count, u'\n'.join(filter)))
                py_count += 1
        
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
                    py_queue.append(u'globals()["__py_parse__"]["{0}_{1}"] = list(__mixed_content__)'.format(py_id, py_count))
                    f.insert(j, mixed_ws+u'{{{0}}}'.format(py_count))
                    py_count += 1
                    i = j
                    mixed_closed = True
                    break
                elif is_directive(_l[0]):
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
                py_queue.append(u'globals()["__py_parse__"]["{0}_{1}"] = list(__mixed_content__)'.format(py_id, py_count))
                f.insert(j, mixed_ws+u'{{{0}}}'.format(py_count))
                py_count += 1
                i = j
        # handle standalone embedded function calls
        elif ':' in l:
            l, inlines = parse_inlines(l)
            if len(inlines) != 0:
                py_queue.append(u'globals()["__py_parse__"]["{0}_{1}"] = fmt.format("""{2}""", {3})'.format(py_id, py_count, l, ','.join(inlines)))
                f.pop(i)
                f.insert(i, ws+u'{{{0}}}'.format(py_count))
                py_count += 1
                i += 1
                continue
        
        i += 1
    
    return f, py_queue


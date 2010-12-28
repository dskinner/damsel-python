#! /usr/bin/env python
# -*- coding: utf-8 -*-
from _sandbox import _open
from _cdoc import parse_ws, sub_str

directives = ['%', '#', '.']

def split_space(s):
    '''
    temporarily from cext, quite silly how this (in cython) is faster than
    split and partition
    '''
    for i, c in enumerate(s):
        if c == u' ':
            return s[:i], s[i+1:]
    return s, u''

def parse_attr(s):
    '''
    temporarily from cext
    '''
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

def _pre_parse(f, implicit=True):
    f = f[:] # this fixes errors for benchmarks with multiple iterative runs
    
    offset = 0
    mark_esc = None
    
    mc = None # mixed content
    mc_ws = None # first plaintxt indention
    
    mf = None # multiline function
    mf_ws = None
    
    for i, line in enumerate(f[:]):
        ### this needs a better way
        if line[:8] == 'extends(':
            _f = _open(line.split("'")[1]).readlines()
            f.pop(0)
            offset -= 1
            
            r = _pre_parse(_f)
            for x in r:
                offset += 1
                f.insert(i+offset, x)
            continue
        ###
        
        ws, l = parse_ws(line)
        
        if not l:
            f.pop(i+offset)
            offset -= 1
            continue
        
        # handle use-cases:
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
        
        # handle multiline function
        if mf is not None:
            if ws <= mf[0]:
                mf[1].append("''')")
                mf[1] = '\n'.join(mf[1])
                f[f.index(mf)] = ''.join(mf)
                mf = None
                mf_ws = None
            else:
                mf_ws = mf_ws or ws
                #ws = ws[:-len(mf_ws)]
                ws = sub_str(ws, mf_ws)
                mf[1].append(ws+l)
                f.pop(i+offset)
                offset -= 1
                continue
        
        #handle mixed content
        if mc is not None:
            if ws <= mc[0] and l[0:4] != 'else':
                mc[1].append('globals()[{__i__}]=list(__mixed_content__)') # __i__ is formatted during _py_parse
                mc[1] = '\n'.join(mc[1]) # build string to prep for py_parse
                f[f.index(mc)] = mc[0]+mc[1] # tack in original ws
                mc = None
                mc_ws = None # do not remove!
            else:
                if l[0] not in ['<', '#', '.', '%']: # more python in other-words
                    mc_ws = None
                    ws = sub_str(ws, mc[0])
                    # is this a list comprehension?
                    if l[0] == '[' and l[-1] == ']':
                        l = '__mixed_content__.extend({0})'.format(l)
                else:
                    mc_ws = mc_ws or ws
                    _ws = sub_str(ws, mc_ws)
                    ws = sub_str(mc_ws, mc[0])
                    #
                    _inlines = []
                    _inline = parse_inline(l)
                    z = 0
                    while _inline is not None:
                        l = l.replace(':'+_inline, '{'+str(z)+'}')
                        _inlines.append(_inline)
                        _inline = parse_inline(l)
                        z += 1
                    #
                    # TODO account for mixed-indention with mixed-plaintxt
                    l = '__mixed_content__.append(fmt.format("""{0}{1}""",{2}))'.format(_ws, l, ','.join(_inlines))

                mc[1].append(ws+l)
                f.pop(i+offset)
                offset -= 1
                continue
        
        if mark_esc is not None:
            f[mark_esc] += l.replace('\\', '')
            f.pop(i+offset)
            offset -= 1
            
            if l[-1] != '\\':
                mark_esc = None
            continue
        
        if implicit and l[0] not in [':', '<', '%', '#', '.', '{', '\\']:
            f.pop(i+offset)
            f.insert(i+offset, ws+':'+l)
            #continue
        
        # inspect for mixed content
        if l[-1] == ':' and l[0] not in ['%', '.', '#', ':']: # temp fix to stop issue 5 until rewrite
            f.pop(i+offset)
            # replace line with list where [0] is orig ws and [1] is string list to be built
            f.insert(i+offset, [ws, [':__mixed_content__ = []', l]])
            mc = f[i+offset]
            continue
        
        # inspect for multiline function
        if l[0] == ':':
            l = l.replace(' ', "(u'''", 1)
            f.pop(i+offset)
            f.insert(i+offset, [ws, [l]])
            mf = f[i+offset]
            continue
        
        if l[-1] == '\\':
            mark_esc = i+offset
            f[mark_esc] = f[mark_esc].replace('\\', '')
        else:
            mark_esc = None
        
    # handle multiline function at document end
    if mf is not None:
        mf[1].append("''')")
        mf[1] = '\n'.join(mf[1])
        f[f.index(mf)] = ''.join(mf)
        mf = None
        mf_ws = None
    # handle mixed content at document end
    if mc is not None:
        mc[1].append('globals()[{__i__}]=list(__mixed_content__)') # __i__ is formatted during _py_parse
        mc[1] = '\n'.join(mc[1]) # prep for py_parse
        f[f.index(mc)] = mc[0]+mc[1]
        mc = None
    return f


if __name__ == '__main__':
    import sys
    from time import time
    import codecs

    __f = sys.argv[1]
    #_f = open(__f).readlines()
    # its faster to .read().splitlines() rather then .readlines()
    _f = codecs.open(__f, 'r', encoding='utf-8').read().splitlines()
    t = sys.argv[2]

    if t == 'y':
        times = []
        for x in range(2000):
            a = time()
            r = _pre_parse(_f)
            times.append(time()-a)
        print min(times)
    elif t == '2':
        r = _pre_parse2(_f)
        for x in r:
            print x
    else:
        r = _pre_parse(_f)
        for x in r:
            print x

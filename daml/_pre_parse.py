#! /usr/bin/env python
# -*- coding: utf-8 -*-
from _sandbox import _open
from _cext import parse_ws, sub_str

def _pre_parse(f):
    """
    TODO normalization to the document to handle all kinds of fun whitespace
    """
    f = f[:] # this fixes errors for benchmarks with multiple iterative runs

    mf = None # multi-line func
    mf_ws = None # first-childs indention

    mc = None # mixed content
    mc_ws = None # first plaintxt indention

    offset = 0
    for i, line in enumerate(f[:]):
        ### this needs a better way
        if i == 0 and line[:9] == ':extends(':
            _f = _open(line.split("'")[1]).readlines()
            r = _pre_parse(_f)
            f.pop(0)
            offset -= 1
            for x in r:
                offset += 1
                f.insert(i+offset, x)
        ###

        ws, l = parse_ws(line)
        if not l:
            f.pop(i+offset)
            offset -= 1
            continue

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

        # handle mixed content
        if mc is not None:
            if ws <= mc[0]:
                mc[1].append('globals()[{__i__}]=list(__mixed_content__)') # __i__ is formatted during _py_parse
                mc[1] = '\n'.join(mc[1]) # prep for py_parse
                f[f.index(mc)] = mc[0]+mc[1]
                mc = None
            else:
                if l[0] == ':':
                    mc_ws = None
                    ws = ws[:-len(mc[0])]
                    l = l[1:]
                    # is this a list comprehension?
                    if l[0] == '[' and l[-1] == ']':
                        l = '__mixed_content__.extend({0})'.format(l)
                else:
                    mc_ws = mc_ws or ws
                    #_ws = ws[:-len(mc_ws)]
                    _ws = sub_str(ws, mc_ws)
                    #ws = mc_ws[:-len(mc[0])]
                    ws = sub_str(mc_ws, mc[0])
                    # TODO account for mixed-indention with mixed-plaintxt
                    l = '__mixed_content__.append(fmt.format("""{0}{1}"""))'.format(_ws, l)


                mc[1].append(ws+l)
                f.pop(i+offset)
                offset -= 1
                continue

        # inspect for mixed content or multiline function
        if l[0] == ':':
            if l[-1] == ':' and l[:4] != ':def': # mixed content
                f.pop(i+offset)
                f.insert(i+offset, [ws, [':__mixed_content__ = []', l[1:]]])
                mc = f[i+offset]
                continue
            elif '(' not in l and '=' not in l: # multiline function
                l = l.replace(' ', "(u'''", 1)
                f.pop(i+offset)
                f.insert(i+offset, [ws, [l]])
                mf = f[i+offset]
                continue

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
    else:
        r = _pre_parse(_f)
        for x in r:
            print x

#! /usr/bin/env python
# -*- coding: utf-8 -*-

def _pre_parse(f):
    result = []

    mf = None # multi-line func
    mf_ws = None # first-childs indention
    
    mc = None # mixed content
    
    for line in f:
        l = line.strip()
        if l == '':
            continue
        
        ws = line.rstrip()[:-len(l)]

        if mf is not None:
            if ws <= mf[0]:
                mf[1].append(')')
                mf[1] = '\n'.join(mf[1])
                mf = None
                mf_ws = None
            else:
                mf_ws = mf_ws or ws
                ws = ws[:-len(mf_ws)]
                mf[1].append(ws+l)
                continue

        ### Heeya
        if mc is not None:
            if l[0] == ':':
                if ws <= mc[0]:
                    mc = None
                else:
                    pass
            else:
                if ws <= mc[0]:
                    mc = None
                else:
                    pass
        ###

        if l[0] == ':':
            if l[-1] == ':':
                result.append([ws, l])
                mc = result[-1]
                continue
            elif '(' not in l and '=' not in l:
                l = l.replace(' ', '(', 1)
                result.append([ws, [l]])
                mf = result[-1]
                continue
        
        result.append([ws, l])

    return result


if __name__ == '__main__':
    import sys
    _f = sys.argv[1]
    f = open(_f).readlines()
    r = _pre_parse(f)
    for x in r:
        print x
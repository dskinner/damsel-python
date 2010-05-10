#! /usr/bin/env python
# -*- coding: utf-8 -*-

def _pre_parse(f):
    """
    TODO normalization to the document to handle all kinds of fun whitespace
    """

    mf = None # multi-line func
    mf_ws = None # first-childs indention

    mc = None # mixed content
    offset = 0
    for i, line in enumerate(f[:]):
        l = line.strip()
        if l == '':
            f.pop(i+offset)
            offset -= 1
            continue

        ws = line.rstrip()[:-len(l)]

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
                ws = ws[:-len(mf_ws)]
                mf[1].append(ws+l)
                f.pop(i+offset)
                offset -= 1
                continue

        # handle mixed content
        if mc is not None:
            if ws <= mc[0]:
                mc[1].append('globals()[{__i__}]=list(__mixed_content__)') # __i__ is formatted during _py_parse
                mc[1] = '\n'.join(mc[1]) # prep for py_parse
                mc = None
            else:
                if l[0] == ':':
                    l = l[1:]
                else:
                    # TODO account for mixed-indention with mixed-plaintxt
                    l = '__mixed_content__.append(fmt.format("""{0}"""))'.format(l)

                ws = ws[:-len(mc[0])]
                mc[1].append(ws+l)
                continue

        # inspect for mixed content or multiline function
        if l[0] == ':':
            if l[-1] == ':': # mixed content
                result.append([ws, [':__mixed_content__ = []', l[1:]]])
                mc = result[-1]
                continue
            elif '(' not in l and '=' not in l: # multiline function
                l = l.replace(' ', "('''", 1)
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
    return f


if __name__ == '__main__':
    import sys
    from time import time
    
    _f = sys.argv[1]
    _f = open(_f).readlines()
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
            print `x`
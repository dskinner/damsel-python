#! /usr/bin/env python
# -*- coding: utf-8 -*-

def _pre_parse(f):
    """
    TODO normalization to the document to handle all kinds of fun whitespace
    """
    result = []

    mf = None # multi-line func
    mf_ws = None # first-childs indention
    
    mc = None # mixed content
    
    for line in f:
        l = line.strip()
        if l == '':
            continue
        
        ws = line.rstrip()[:-len(l)]

        # handle multiline function
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

        # handle mixed content
        if mc is not None:
            if ws <= mc[0]:
                mc[1].append('globals()["__py_evals__"][{__i__}]=list(__mixed_content__)') # __i__ is formatted during _py_parse
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
#! /usr/bin/env python
# -*- coding: utf-8 -*-
from collections import deque
import __builtin__
from _fmt import DamlFormatter

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
                l = l.replace(' ', '(', 1)
                result.append([ws, [l]])
                mf = result[-1]
                continue

        result.append([ws, l])

    return result


def include(f):
    """
    FIXME this, and all functions need to be made to go to globals() either in pre_parse or in py_parse
    """
    f = open(f).readlines()
    f = _pre_parse(f)
    f = _py_parse(f)
    return f

sandbox = { '__builtins__': None,
            '__blocks__': {},
            '__py_evals__': {}, # need to index by filename, then line number
            'dict': __builtin__.dict,
            'enumerate': __builtin__.enumerate,
            'fmt': DamlFormatter(),
            'globals': __builtin__.globals,
            'len': __builtin__.len,
            'list': __builtin__.list,
            'locals': __builtin__.locals,
            'map': __builtin__.map,
            'max': __builtin__.max,
            'min': __builtin__.min,
            'open': __builtin__.open,
            'range': __builtin__.range,
            'include': include}

def block(s):
    s = s.splitlines()
    s = _py_parse(s)
    globals()['__blocks__'][s[0]] = [s[1:], False] # [content, been-used-yet?]

def _py_parse(f):
    queue = deque()
    _id = id(f)

    for i, (ws, l) in enumerate(f):
        if l[0] == ':':
            a = l.find('(')
            b = l.find('=')
            if b != -1 and (b < a or a == -1):
                """
                :mine('asdf')
                :get('func=blah')
                :test = 'tad(a)'
                :title = 'woah'
                """
                l = l[1:]
            elif '{__i__}' in l:
                l = l.replace('{__i__}', '"__{0}_{1}__"'.format(_id, i), 1)[1:]
            else:
                l = 'globals()["__{0}_{1}__"] = {2}'.format(_id, i, l[1:])
            queue.append((i, l))
            continue

        if '{' in l:
            queue.append((i, 'globals()["__{0}_{1}__"] = fmt.format("""{2}""")'.format(_id, i, l)))
            continue

        # look to see if :func() is embedded in line
        if ':' in l:
            a = l.index(':')
        else:
            continue
        if '(' in l:
            b = l.index('(')
        else:
            continue
        if ' ' in l[a:b] or a > b: # check a>b for attributes that have :
            continue

        c = l.index(')')+1
        queue.append((i, 'globals()["__{0}_{1}__"] = {2}'.format(_id, i, l[a+1:c]))) # FIXME embedded needs a line number among other things

    py_str = '\n'.join([x[1] for x in queue])
    #print py_str
    #print '@@@'
    eval(compile('fmt.namespace=globals()\n'+py_str, '<string>', 'exec'), sandbox)

    offset = 0
    while queue:
        i, l = queue.popleft()

        k = '__{0}_{1}__'.format(_id, i)
        if k in sandbox:
            r = sandbox[k]

            if isinstance(r, list):
                ws, tmp = f.pop(i+offset)
                for x in r:
                    if isinstance(x, list):
                        y_ws, y = x
                        f.insert(i+offset, (ws+y_ws, y))
                        offset += 1
                    else:
                        f.insert(i+offset, (ws, x))
                        offset += 1
                offset -= 1
            else:
                f[i+offset][1] = r
        else:
            f.pop(i+offset)
            offset -= 1

    return f


if __name__ == '__main__':
    import sys
    from time import time

    _f = sys.argv[1]
    t = sys.argv[2]
    f = open(_f).readlines()

    if t == 'yes':
        times = []
        for x in range(2000):
            a = time()
            _py_parse(_pre_parse(f))
            times.append(time()-a)
        print min(times)
    else:

        f = open(_f).readlines()
        f = _pre_parse(f)
        f = _py_parse(f)

        for x in f:
            print x


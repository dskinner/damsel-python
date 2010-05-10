#! /usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque
import _sandbox

def _py_parse(f):
    queue = deque()
    sandbox = _sandbox.new()

    for i, (ws, l) in enumerate(f):
        if l[0] == ':':
            if '{__i__}' in l:
                l = l.replace('{__i__}', str(i), 1)
            queue.append((i, l[1:]))
            continue

        if '{' in l:
            queue.append((i, 'globals()["__py_evals__"][{0}] = fmt.format("""{1}""")'.format(i, l)))
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
        queue.append((i, l[a+1:c]))

    py_str = '\n'.join([x[1] for x in queue])
    #print py_str
    eval(compile('fmt.namespace=globals()\n'+py_str, '<string>', 'exec'), sandbox)

    offset = 0
    while queue:
        i, l = queue.popleft()
        if i in sandbox['__py_evals__']:
            r = sandbox['__py_evals__'][i]
            if isinstance(r, list):
                ws, tmp = f.pop(i+offset)
                for x in r:
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
    from _pre_parse import _pre_parse
    import sys
    
    _f = sys.argv[1]
    f = open(_f).readlines()
    f = _pre_parse(f)
    f = _py_parse(f)
    
    for x in f:
        print x


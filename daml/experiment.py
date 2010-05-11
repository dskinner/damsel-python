#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from _element2 import Element

def parse(f):
    result = []
    els = ('%', '.', '#')
    prev = None
    m = {}

    for line in f:
        line = line.rstrip()
        if line == '':
            continue

        l = line.lstrip()
        ws = line[:-len(l)]

        if l[0] in els:
            e = Element(l)

            if prev is None:
                pass
            elif ws > prev:
                result[-1][1].append(e)
                m[ws] = len(result)
            elif ws == prev:
                result[-1][1].parent.append(e)
                m[ws] = len(result)
            else:
                j = m[ws]
                result[j][1].parent.append(e)
                for k in m.keys():
                    if k > ws:
                        del m[k]
                m[ws] = len(result)

            result.append((ws, e))
            prev = ws
    return result


if __name__ == '__main__':
    _f = sys.argv[1]
    
    from time import time
    times = []
    for x in range(200):
        f = open(_f)
        a = time()
        result = parse(f)
        result[0][1].to_string()
        times.append(time()-a)
    print min(times)
    

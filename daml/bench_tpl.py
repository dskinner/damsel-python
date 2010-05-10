#! /usr/bin/env python
# -*- coding: utf-8 -*-
from _parse import parse

if __name__ == '__main__':
    from time import time
    import sys

    f = sys.argv[1]
    f = open(f).readlines()
    
    r = parse(f)
    print(r)
    
    times = []
    for x in range(200):
        a = time()
        parse(f)
        times.append(time()-a)
    print(min(times))
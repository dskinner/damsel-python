# -*- coding: utf-8 -*-
"""
eval('len("asdf")', {"__builtins__":None}, {'len': __builtin__.len})
"""
from time import time
times = []
for x in range(20):
    a = time()
    for y in range(1000):
        eval('y+20', {'y': y})
    times.append(time()-a)
print min(times)
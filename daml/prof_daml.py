#! /usr/bin/env python
# -*- coding: utf-8 -*-

from _parse import Template, parse
from time import time

f = 'template.daml'
data = dict(title='Just a test', user='joe', items=['Number %d' % num for num in range(1, 15)])

tpl = Template(f)

times = []
for x in range(10):
    a = time()
    tpl.render(data)
    times.append(time()-a)
print min(times)

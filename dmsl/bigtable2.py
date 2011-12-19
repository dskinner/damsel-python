from _parse import Template

table = [dict(a=1,b=2,c=3,d=4,e=5,f=6,g=7,h=8,i=9,j=10)
          for x in range(1000)]

f = u"""
table = [['%tr'] + ['  %td '+str(col) for col in row.values()] for row in kwargs['table']]

'''
flatten result
'''
result = [x for y in table for x in y]

%table
    result
""".splitlines()

def func(): pass
func = type(func)

import pprint
from _pre import _pre
from _py import _compile
import _sandbox
from time import time
from cdoc2 import doc_pre, doc_py, _build_from_parent, _build_element

def _post(s):
    return '<!DOCTYPE html>'+s.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')

def get_ms(sec):
    return '%.2f ms' % (sec*1000)

sandbox = {}
sandbox.update(_sandbox.default_sandbox)
sandbox['kwargs'] = {'table': table}

fn = 'string'

a = time()
r, py_q = _pre(f)
print '_pre', get_ms(time()-a)


a = time()
code, py_str = _compile(py_q, fn)
print '_compile', get_ms(time()-a)


a = time()
code = func(code.co_consts[0], sandbox)
print 'func', get_ms(time()-a)


a = time()
r = doc_pre(r)
print '_doc_pre', get_ms(time()-a)
print 'r1', r.to_string()
from copy import copy, deepcopy
r2 = copy(r)
print 'r2', r.to_string()

a = time()
py_locals = code()
print 'code', get_ms(time()-a)

###################################################
a = time()
py_list = r.findall(u'_py_')
py_id = id(py_q)
py_parse = py_locals['__py_parse__']
print 'inspect py', get_ms(time()-a)

a = time()
'''
for e in py_list:
    t = e.get_text()[1:-1]
    k = u'{0}_{1}'.format(py_id, t)
    o = py_parse[k]
    if isinstance(o, (list, tuple)):
        p = e.get_parent()
        index = None
        if len(p.get_children()) != 0:
            index = p.get_children().index(e)
        p.get_children().remove(e)
        _build_from_parent(p, index, [unicode(x) for x in o])
    else:
        _build_element(e, unicode(o))
'''
doc_py(r, py_id, py_parse)
print 'custom', get_ms(time()-a)
######################################################

import lxml.etree as etree

a = time()
#result = etree.tostring(r)
result = r.to_string()
print 'tostring', get_ms(time()-a)

a = time()
result = _post(result)
print '_post', get_ms(time()-a)



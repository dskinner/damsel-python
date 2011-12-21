from _parse import Template

table = [dict(a=1,b=2,c=3,d=4,e=5,f=6,g=7,h=8,i=9,j=10)
          for x in range(1000)]

f = u"""
table = [['%tr'] + ['  %td '+str(col) for col in row.values()] for row in kwargs['table']]
%table [x for y in table for x in y]
""".splitlines()

f = u"""
%table for row in table:
    %tr for col in row.values():
        %td {col}
""".splitlines()

def func(): pass
func = type(func)

import pprint
from _pre import _pre
from _py import _compile
import _sandbox
from time import time
from cdoc2 import doc_pre, doc_py
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4)

def _post(s):
    return '<!DOCTYPE html>'+s.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')

def get_ms(sec):
    return '%.2f ms' % (sec*1000)

sandbox = {}
sandbox.update(_sandbox.default_sandbox)
sandbox['table'] = table

fn = 'string'

a = time()
r, py_q = _pre(f)
print '_pre', get_ms(time()-a)

a = time()
code, py_str = _compile(py_q, fn)
print '_compile', get_ms(time()-a)
print py_str

a = time()
code = func(code.co_consts[0], sandbox)
print 'func', get_ms(time()-a)


a = time()
r = doc_pre(r)
print '_doc_pre', get_ms(time()-a)

a = time()
py_locals = code()
print 'code', get_ms(time()-a)

###################################################
a = time()
py_id = id(py_q)
py_parse = py_locals['__py_parse__']
print 'inspect py', get_ms(time()-a)

a = time()
doc_py(r, py_id, py_parse)
print 'doc_py', get_ms(time()-a)
######################################################

a = time()
#result = etree.tostring(r)
result = str(r)
print 'tostring', get_ms(time()-a)

a = time()
result = _post(result)
print '_post', get_ms(time()-a)


#! /usr/bin/env python
# -*- coding: utf-8 -*-
from copy import copy, deepcopy
from lxml.etree import tostring
#from xml.etree.cElementTree import tostring

import _sandbox
from _pre import _pre
from _py import _compile
from cdoc import _doc_pre, _build_from_parent, _build_element

def func():pass
func = type(func)

class Template(object):
    def __init__(self, filename):
        self.sandbox = {}
        if isinstance(filename, list):
            self.f = filename
        else:
            self.f = _sandbox._open(filename).read().splitlines()
        self.r, self.py_q = _pre(self.f)
        if len(self.py_q) == 0:
            self.code = None
        else:
            self.code = _compile(self.py_q)
            self.code = func(self.code.co_consts[0], self.sandbox)
        self.r = _doc_pre(self.r)
    
    def render(self, **kwargs):
        self.sandbox.clear()
        self.sandbox.update(_sandbox.default_sandbox)
        self.sandbox.update(_sandbox.extensions)
        self.sandbox['kwargs'] = kwargs

        r = copy(self.r)
        
        if self.code == None:
            return _post(tostring(r))
        
        py_list = r.findall('.//_py_')
        py_id = id(self.py_q)
        py_locals = self.code()
        py_parse = py_locals['__py_parse__']
        
        for e in py_list:
            t = e.text[1:-1]
            k = u'{0}_{1}'.format(py_id, t)
            o = py_parse[k]
            if isinstance(o, (list, tuple)):
                p = e.getparent()
                
                index = None
                if len(p.getchildren()) != 0:
                    index = p.getchildren().index(e)
                
                p.remove(e)
                _build_from_parent(p, index, [unicode(x) for x in o])
            else:
                _build_element(e, unicode(o))
        
        return _post(tostring(r))

def _post(s):
    return '<!DOCTYPE html>'+s.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')

if __name__ == '__main__':
    import sys
    import codecs
    from time import time
    _f = sys.argv[1]
    #print parse(_f)
    t = Template(_f)
    if '-p' in sys.argv:
        def run():
            for x in range(2000):
                t.render()
        import cProfile, pstats
        prof = cProfile.Profile()
        prof.run('run()')
        stats = pstats.Stats(prof)
        stats.strip_dirs()
        stats.sort_stats('cumulative')
        stats.print_stats(25)
    else:
        print t.render()


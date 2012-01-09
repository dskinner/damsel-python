#! /usr/bin/env python
# -*- coding: utf-8 -*-
from copy import copy, deepcopy

import _sandbox
from _pre import _pre
from _py import _compile
from cdoc import doc_pre, doc_py

def func():pass
func = type(func)

class RenderException(Exception):
    def __init__(self, f, py_str, exc_type, exc_value, exc_traceback):
        import traceback
        tb = traceback.extract_tb(exc_traceback)
        self.msg = ['']
        py_str = py_str.split('\n')

        for line in tb:
            fn = line[0]
            ln = line[1]
            fnc = line[2]
            src = line[3]
            try:
                src = py_str[ln].strip()
                for i, x in enumerate(f):
                    if src in x:
                        ln = i
                        break
            except:
                pass
            self.msg.append('  File {0}, line {1}, in {2}\n    {3}'.format(fn, ln, fnc, src))
        self.msg.append(repr(exc_value))
        #self.msg.append('\n--- DMSL PYTHON QUEUE ---')
        #self.msg.extend(py_q)
        self.msg = '\n'.join(self.msg)

    def __str__(self):
        return self.msg


class Template(object):
    debug = False

    def __init__(self, filename):
        self.sandbox = _sandbox.new()
        self.sandbox.update(_sandbox.extensions)

        if isinstance(filename, list):
            self.f = filename
            self.fn = '<string>'
        else:
            self.f = _sandbox._open(filename).read().splitlines()
            self.fn = filename

        self.r, self.py_q = _pre(self.f)
        self.r = doc_pre(self.r)

    def render(self, *args, **kwargs):
        self.sandbox['args'] = args

        r = copy(self.r)

        if len(self.py_q) == 0:
            return r.tostring()
        else:
            self.code, self.py_str = _compile(self.py_q, self.fn, kwargs)
            self.code = func(self.code.co_consts[0], self.sandbox)

        try:
            py_locals = self.code(**kwargs)
        except Exception as e:
            if isinstance(e, TypeError) or isinstance(e, KeyError):
                import sys
                if self.debug:
                    print self.py_str
                raise RenderException(self.f, self.py_str, *sys.exc_info())
            else:
                raise e

        # Check for empty doc, ussually result of python only code
        if r is None:
            return ''

        py_id = id(self.py_q)
        py_parse = py_locals['__py_parse__']
        doc_py(r, py_id, py_parse)
        return r.tostring()


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


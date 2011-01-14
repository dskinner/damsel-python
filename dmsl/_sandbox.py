# -*- coding: utf-8 -*-

try:
    import __builtin__
except ImportError:
    import builtins as __builtin__ #Python 3.0

from copy import copy
import os.path
from cfmt import DMSLFormatter
import codecs

### Default set of dmsl extensions
def css(s):
    s = s.splitlines()
    n = s[0]
    s = s[1:]
    return [u'%link[rel=stylesheet][href={0}{1}]'.format(n, x) for x in s]

def js(s):
    s = s.splitlines()
    n = s[0]
    s = s[1:]
    return ['%script[src={0}{1}]'.format(n, x) for x in s]
###

def _open(f):
    return codecs.open(os.path.join(_open.template_dir, f), encoding='utf-8', errors='replace')
_open.template_dir = ''

default_sandbox = { '__builtins__': None,
                    'css': css,
                    'dict': __builtin__.dict,
                    'enumerate': __builtin__.enumerate,
                    'float': __builtin__.float,
                    'fmt': DMSLFormatter(),
                    'globals': __builtin__.globals,
                    'int': __builtin__.int,
                    'js': js,
                    'len': __builtin__.len,
                    'list': __builtin__.list,
                    'locals': __builtin__.locals,
                    'map': __builtin__.map,
                    'max': __builtin__.max,
                    'min': __builtin__.min,
                    'open': _open,
                    'range': __builtin__.range,
                    'sorted': __builtin__.sorted,
                    'str': __builtin__.str}

# Python3
if hasattr(__builtin__, 'False'):
    default_sandbox['False'] = getattr(__builtin__, 'False')

if hasattr(__builtin__, 'True'):
    default_sandbox['True'] = getattr(__builtin__, 'True')
#

def new():
    return copy(default_sandbox)

extensions = {}
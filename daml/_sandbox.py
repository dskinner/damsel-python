# -*- coding: utf-8 -*-

try:
    import __builtin__
except ImportError:
    import builtins as __builtin__ #Python 3.0

from copy import copy

from _fmt import DamlFormatter

class LXML(object):
    """
    Used to declare lxml.etree.tostring params by declaring attributes. This
    ends up working faster then declaring variables and scraping and is easier
    on the eyes and fingers for declaring common tostring keyword arguments
    versus the use of a traditional dict.
    """
    pass

default_sandbox = { '__builtins__': None,
                    '__blocks__': {},
                    '__py_evals__': {}, # need to index by filename, then line number
                    'dict': __builtin__.dict,
                    'enumerate': __builtin__.enumerate,
                    'fmt': DamlFormatter(),
                    'globals': __builtin__.globals,
                    'len': __builtin__.len,
                    'list': __builtin__.list,
                    'locals': __builtin__.locals,
                    'map': __builtin__.map,
                    'max': __builtin__.max,
                    'min': __builtin__.min,
                    'open': __builtin__.open,
                    'range': __builtin__.range,
                    'lxml': LXML()}

# Python3
if hasattr(__builtin__, 'False'):
    default_sandbox['False'] = getattr(__builtin__, 'False')

if hasattr(__builtin__, 'True'):
    default_sandbox['True'] = getattr(__builtin__, 'True')
#

def new():
    return copy(default_sandbox)
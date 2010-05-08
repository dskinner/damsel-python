# -*- coding: utf-8 -*-

class LXML(object):
    """
    Used to declare lxml.etree.tostring params by declaring attributes. This
    ends up working faster then declaring variables and scraping and is easier
    on the eyes and fingers for declaring common tostring keyword arguments
    versus the use of a traditional dict.
    """
    pass

class Sandbox(object):
    pass


safe_globals = {'__builtins__': None,
                '__blocks__': {},
                'dict': __builtin__.dict,
                'enumerate': __builtin__.enumerate,
                'globals': __builtin__.globals,
                'len': __builtin__.len,
                'list': __builtin__.list,
                'locals': __builtin__.locals,
                'open': safe_open, # FIXME make a safe wrapper for opening additional theme files safely
                'map': __builtin__.map,
                'min': __builtin__.min,
                'max': __builtin__.max,
                'range': __builtin__.range,
                'block': block,
                'include': include,
                'parse_py': parse_py,
                'lxml': LXML()}

# Python3
if hasattr(__builtin__, 'False'):
    safe_globals['False'] = getattr(__builtin__, 'False')

if hasattr(__builtin__, 'True'):
    safe_globals['True'] = getattr(__builtin__, 'True')
#
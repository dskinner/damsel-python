#from _parse_pre import _parse_pre
from _pre import _pre

def _compile(py_queue, fn, kwargs):
    py_str = '\n  '.join(py_queue)
    if py_str == '':
        return None
    arg_list = ','.join([key for key in kwargs.keys()])
    py_str = 'def _py('+arg_list+'):\n  __py_parse__, __blocks__ = {}, {}\n  '+py_str+'\n  return locals()'
    return compile(py_str, fn, 'exec'), py_str


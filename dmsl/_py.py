#from _parse_pre import _parse_pre
from _pre import _pre

def _compile(py_queue):
    py_str = '\n  '.join(py_queue)
    if py_str == '':
        return None
    py_str = 'def _py(**kwargs):\n  __py_parse__, __blocks__ = {}, {}\n  fmt.namespace=globals()\n  '+py_str+'\n  return locals()'
    return compile(py_str, '<string>', 'exec')
#from _parse_pre import _parse_pre
from _pre import _pre
from _sandbox import block

def func():pass
func = type(func)

def _compile(py_queue):
    py_str = '\n  '.join(py_queue)
    if py_str == '':
        return None
    py_str = 'def _py(**kwargs):\n  __py_parse__ = {}\n  fmt.namespace=globals()\n  '+py_str+'\n  return locals()'
    return compile(py_str, '<string>', 'exec')

def _py(_f, py_queue, sandbox, local=None, code=None):
    f = _f[:]
    if code is None:
        code = _compile(py_queue)
        if code is None:
            return f
    if local is not None:
        sandbox.update(local)
    c = func(code.co_consts[0], sandbox)
    py_locals = c()
    py_parse = py_locals['__py_parse__']
    
    i = 0
    py_count = 0
    py_id = id(py_queue)
    while i < len(f):
        if isinstance(f[i], tuple):
            i += 1
            continue
        t = u'{%s}' % py_count
        if t in f[i]:
            # these should always be blank lines... i think...
            
            k = u'{0}_{1}'.format(py_id, py_count)
            o = py_parse[k]
            
            if isinstance(o, (list, tuple)):
                ws = f.pop(i).replace(t, u'')
                for x in o:
                    f.insert(i, ws+x)
                    i += 1
                py_count += 1
                continue
            else:
                f[i] = f[i].replace(t, o)
                i += 1
                py_count += 1
                continue
        elif u'{block}' in f[i]:
            tmp = f[i]
            tmp = tmp.replace(u'{block}', u'')
            name = tmp[tmp.index(u'{')+1:tmp.index(u'}')]
            if name in block.blocks:
                ws = f.pop(i).replace(u'{block}{'+name+u'}', u'')
                block_f, block_q = _pre(block.blocks[name])
                block_r = _py(block_f, block_q, sandbox, py_locals)
                for x in block_r:
                    f.insert(i, ws+x)
                    i += 1
                del block.blocks[name]
                continue
            else:
                f.pop(i)
                continue
        i += 1
    
    return f


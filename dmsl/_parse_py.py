from _parse_pre import _parse_pre
from _ext import block

def _parse_py(_f, py_queue, sandbox):
    f = _f[:]
    
    py_str = u'\n'.join(py_queue)
    if py_str == u'':
        return f
    try:
        cc = compile(u'if "__py_parse__" not in globals():\n globals()["__py_parse__"] = {}\nfmt.namespace=globals()\n'+py_str, u'<string>', u'exec')
        eval(cc, sandbox)
    except Exception as e:
        print '=================='
        print 'Compilation String'
        print '=================='
        print py_str
        print '------------------'
        raise e
    
    i = 0
    py_count = 0
    py_id = id(py_queue)
    while i < len(f):
        t = u'{%s}' % py_count
        if t in f[i]:
            # these should always be blank lines... i think...
            
            k = u'{0}_{1}'.format(py_id, py_count)
            o = sandbox[u'__py_parse__'][k]
            
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
                block_f, block_q = _parse_pre(block.blocks[name])
                block_r = _parse_py(block_f, block_q, sandbox)
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


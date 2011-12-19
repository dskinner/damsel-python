cdef object Element, SubElement
from lxml.etree import Element, SubElement
#from xml.etree.cElementTree import Element, SubElement
from _cutils cimport _parse_ws, _parse_attr, _parse_tag, _split_space

def _doc_pre(f):
    root = Element('root')
    r = {}
    _ids = {}
    prev = None
    plntxt = {}
    for line in f:
        ws, l = _parse_ws(line)
        
        ### plntxt queue
        if l[0] == u'\\':
            if ws in plntxt:
                plntxt[ws].append(l[1:])
            else:
                plntxt[ws] = [l[1:]]
            continue
        if plntxt:
            for _ws, text in plntxt.items():
                text = ' '+' '.join(text)
                el = r[prev]
                if _ws > prev:
                    el.text += text
                else: # _ws == prev
                    el.tail = el.tail and el.tail+text or text
            plntxt = {}
        ###
        
        if l[0] == u'{':
            if ws == u'': # TODO use cases of no root node will make troublesome
                continue
            _tag, _id, _class, attr, text = u'_py_', u'', u'', None, l
        else:
            u, attr = _parse_attr(l)
            hash, text = _split_space(u)
            _tag, _id, _class = _parse_tag(hash)
        
        if ws == u'':
            if _id in _ids:
                e = _ids[_id]
                if attr.pop('super', None) is None:
                    for child in e.getchildren():
                        e.remove(child)
            else:
                e = SubElement(root, _tag or 'div')
        elif ws > prev:
            e = SubElement(r[prev], _tag or 'div')
        elif ws == prev:
            e = SubElement(r[prev].getparent(), _tag or 'div')
        elif ws < prev:
            e = SubElement(r[ws].getparent(), _tag or 'div')
            
            for _ws in r.keys():
                if _ws > ws:
                    r.pop(_ws)
        
        e.text = text
        if _id:
            e.attrib['id'] = _id
            _ids[_id] = e
        if _class:
            e.attrib['class'] = _class
        if attr:
            e.attrib.update(attr)
        
        r[ws] = e
        prev = ws
    
    if len(root) is 0:
        return None

    return root[0]

def _build_element(e, line):
    ws, l = _parse_ws(line)
        
    u, attr = _parse_attr(l)
    hash, text = _split_space(u)
    _tag, _id, _class = _parse_tag(hash)
    
    e.tag = _tag or u'div'
    e.text = text
    if _id:
        e.attrib['id'] = _id
    if _class:
        e.attrib['class'] = _class
    if attr:
        e.attrib.update(attr)

def _build_from_parent(p, index, f):
    # TODO this is one of the slowest parts of dmsl for extremely large documents
    r = {'root': p}
    prev = ''
    plntxt = {}
    from time import time
    ws_time = 0
    plntxt_time = 0
    tag_time = 0
    el_time = 0
    attrib_time = 0

    for line in f:
        st = time()
        ws, l = _parse_ws(line)
        ws_time += time()-st

        ### plntxt queue
        st = time()
        if l[0] == u'\\':
            if ws in plntxt:
                plntxt[ws].append(l[1:])
            else:
                plntxt[ws] = [l[1:]]
            continue
        if plntxt:
            for _ws, text in plntxt.items():
                text = ' '+' '.join(text)
                el = r[prev]
                if _ws > prev:
                    el.text += text
                else: # _ws == prev
                    el.tail = el.tail and el.tail+text or text
            plntxt = {}
        plntxt_time += time()-st
        ###
        
        st = time()
        u, attr = _parse_attr(l)
        hash, text = _split_space(u)
        _tag, _id, _class = _parse_tag(hash)
        tag_time += time()-st
        
        st = time()
        if ws == u'':
            _p = None
            e = SubElement(p, _tag or 'div')
        elif ws > prev:
            _p = r[prev]
            e = SubElement(_p, _tag or 'div')
        elif ws == prev:
            _p = r[prev].getparent()
            e = SubElement(_p, _tag or 'div')
        elif ws < prev:
            _p = r[ws].getparent()
            e = SubElement(_p, _tag or 'div')
            
            for _ws in r.keys():
                if _ws > ws:
                    r.pop(_ws)
        
        el_time += time()-st
        
        st = time()
        # fctr 7
        if index is not None and _p is None:
            p.insert(index, e)
            index += 1
        st = time()
        # fctr 5
        e.text = text
        if _id:
            e.attrib['id'] = _id
        if _class:
            e.attrib['class'] = _class
        if attr:
            e.attrib.update(attr)
        # fctr 1
        r[ws] = e
        # fctr 1.5
        prev = ws
        attrib_time += time()-st
    
    print '!!!!!'
    print 'ws_time: %.2f ms' % (ws_time*1000)
    print 'plntxt_time: %.2f ms' % (plntxt_time*1000)
    print 'tag_time: %.2f ms' % (tag_time*1000)
    print 'el_time: %.2f ms' % (el_time*1000)
    print 'attrib_time: %.2f ms' % (attrib_time*1000)
    print '!!!!!'

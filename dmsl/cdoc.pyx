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
        if attr is not None:
            e.attrib.update(attr)
        
        r[ws] = e
        prev = ws
    
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
    if attr is not None:
        e.attrib.update(attr)

def _build_from_parent(p, index, f):
    r = {'root': p}
    prev = ''
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
    
        u, attr = _parse_attr(l)
        hash, text = _split_space(u)
        _tag, _id, _class = _parse_tag(hash)
        
        if ws == u'':
            _p = r['root']
            e = SubElement(_p, _tag or 'div')
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
        
        if index is not None and _p == p:
            p.insert(index, e)
            index += 1
        
        e.text = text
        if _id:
            e.attrib['id'] = _id
        if _class:
            e.attrib['class'] = _class
        if attr is not None:
            e.attrib.update(attr)
        
        r[ws] = e
        prev = ws


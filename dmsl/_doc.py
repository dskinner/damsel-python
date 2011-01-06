from lxml.etree import Element, SubElement
#from xml.etree.cElementTree import Element, SubElement
from utils import parse_ws, parse_attr, split_space, split_pound, split_period, parse_tag, is_directive

def _doc_pre(f):
    root = Element('root')
    r = {}
    _ids = {}
    prev = None
    for line in f:
        ws, l = parse_ws(line)
        
        if l[0] == '{':
            _tag, _id, _class, attr, text = '_py_', False, False, None, l
        else:
            u, attr = parse_attr(l)
            hash, text = split_space(u)
            _tag, _id, _class = parse_tag(hash)
        
        if ws == '':
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
    ws, l = parse_ws(line)
        
    u, attr = parse_attr(l)
    hash, text = split_space(u)
    _tag, _id, _class = parse_tag(hash)
    
    e.tag = _tag or 'div'
    e.text = text
    if _id:
        e.attrib['id'] = _id
    if _class:
        e.attrib['class'] = _class
    if attr is not None:
        e.attrib.update(attr)

def _build_from_parent(p, f):
    r = {'root': p}
    prev = ''
    
    for line in f:
        ws, l = parse_ws(line)
        
        u, attr = parse_attr(l)
        hash, text = split_space(u)
        _tag, _id, _class = parse_tag(hash)
        
        if ws == '':
            e = SubElement(r['root'], _tag or 'div')
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
        if _class:
            e.attrib['class'] = _class
        if attr is not None:
            e.attrib.update(attr)
        
        r[ws] = e
        prev = ws


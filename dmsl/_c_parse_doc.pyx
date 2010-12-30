# -*- coding: utf-8 -*-

cdef object Element, SubElement
from lxml.etree import Element, SubElement
from _c_parse_ext cimport parse_ws, parse_attr, split_space, split_pound, split_period, parse_tag, is_directive

def _parse_doc(f):
    cdef unicode ws, _ws, l, _tag, _id, _class
    cdef object e, e_root

    r = {u'': Element(u'html')}
    plntxt = {}

    prev = u''

    for line in f[1:]:
        ws, l = parse_ws(line)
        
        ### plntxt queue
        if not is_directive(l[0]):
            if ws in plntxt:
                plntxt[ws].append(l)
            else:
                plntxt[ws] = [l]
            continue
        
        if plntxt:
            for _ws, text in plntxt.items():
                text = u' '.join(text)
                el = r[prev]
                if _ws > prev:
                    el.text += ' '+text
                else: # _ws == prev
                    el.tail = el.tail and el.tail+' '+text or text
            plntxt = {}
        ###
        
        u, attr = parse_attr(l)
        u = split_space(u)
        _tag, _id, _class = parse_tag(u[0])
        
        # 
        if ws > prev:
            e_root = r[prev]
        if ws == prev:
            e_root = r[prev].getparent()
        if ws < prev:
            e_root = r[ws].getparent()
            
            for _ws in r.keys():
                if _ws > ws:
                    r.pop(_ws)
        
        e = SubElement(e_root, _tag or u'div')
        e.text = u[1]
        if _id:
            e.attrib[u'id'] = _id
        if _class:
            e.attrib[u'class'] = _class
        if attr is not None:
            e.attrib.update(attr)
        
        r[ws] = e
        prev = ws
        
        
    if plntxt:
        for _ws, text in plntxt.items():
            text = u' '.join(text)
            el = r[prev]
            if _ws > prev:
                el.text += ' '+text
            else: # _ws == prev
                el.tail = el.tail and el.tail+' '+text or text
    return r[u'']


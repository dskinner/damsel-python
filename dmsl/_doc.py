from lxml.etree import Element, SubElement
from utils import parse_ws, parse_attr, split_space, split_pound, split_period, parse_tag, is_directive

def _doc_pre(_f):
    f = _f[:]
    
    for i, line in enumerate(f):
        if isinstance(line, tuple):
            continue
        
        ws, l = parse_ws(line)
        
        if l[0] == '{':
            continue
        
        u, attr = parse_attr(l)
        hash, text = split_space(u)
        _tag, _id, _class = parse_tag(hash)
        
        f[i] = (ws, _tag, _id, _class, attr, text)
    
    return f

def _doc_build(f):
    r = {}
    prev = None

    for line in f:
        ws, _tag, _id, _class, attr, text = line
        
        #
        if prev is None:
            e = Element(_tag)
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
    return r['']

def _doc(f):
    r = {}
    plntxt = {}

    prev = None

    for line in f:
        ws, l = parse_ws(line)
        
        ### plntxt queue, TODO i dont think this is relevant anymore
        if not is_directive(l[0]):
            if ws in plntxt:
                plntxt[ws].append(l)
            else:
                plntxt[ws] = [l]
            continue
        
        if plntxt:
            for _ws, text in plntxt.items():
                text = ' '.join(text)
                el = r[prev]
                if _ws > prev:
                    el.text += ' '+text
                else: # _ws == prev
                    el.tail = el.tail and el.tail+' '+text or text
            plntxt = {}
        ###
        
        u, attr = parse_attr(l)
        hash, text = split_space(u)
        _tag, _id, _class = parse_tag(hash)
        
        #
        if prev is None:
            e = Element(_tag)
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
        
        
    if plntxt:
        for _ws, text in plntxt.items():
            text = ' '.join(text)
            el = r[prev]
            if _ws > prev:
                el.text += ' '+text
            else: # _ws == prev
                el.tail = el.tail and el.tail+' '+text or text
    return r['']


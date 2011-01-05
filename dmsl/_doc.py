from lxml.etree import Element, SubElement
from utils import parse_ws, parse_attr, split_space, split_pound, split_period, parse_tag, is_directive

def _doc2(_f):
    f = _f[:]
    r = {'': Element('html')}
    f[0] = r['']
    plntxt = {}

    prev = u''

    for i, line in enumerate(f):
        # TODO stop this at once!!
        if i == 0:
            continue
        
        ws, l = parse_ws(line)
        
        if l[0] == '{': # TODO this hardly a good way to check
            _tag = 'py'
            text = l
            _id = False
            _class = False
            attr = None
        else:
            u, attr = parse_attr(l)
            hash, text = split_space(u)
            _tag, _id, _class = parse_tag(hash)
        
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
        e.text = text
        if _id:
            e.attrib[u'id'] = _id
        if _class:
            e.attrib[u'class'] = _class
        if attr is not None:
            e.attrib.update(attr)
        
        r[ws] = e
        f[i] = e
        prev = ws
    return f

def _build(l):
    pass

def _doc(f):
    r = {u'': Element(u'html')}
    plntxt = {}

    prev = u''

    for line in f[1:]:
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


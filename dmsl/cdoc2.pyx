from _cutils cimport _parse_ws, _parse_attr, _parse_tag, _split_space
from copy import copy

cdef inline _findall(Element el, unicode srch, list result):
    cdef Element child

    for child in el._children:
        if child._tag == srch:
            result.append(child)
        if len(child._children) != 0:
            _findall(child, srch, result)

cdef inline unicode _tostring(Element el):
    cdef Element child
    cdef unicode s
    cdef list keyset = []
    cdef list attribset = []

    s = u'<' + el._tag

    if el._attrib:
        el._attrib.reverse()
        for k, v in el._attrib:
            if k in keyset:
                continue
            attribset.append((k, v))
            keyset.append(k)
        attribset.reverse()
        s += u''.join([u' '+k+u'="'+v+u'"' for k, v in attribset])#.items()])

    s += u'>' + el._text + u''.join([_tostring(child) for child in el._children]) + u'</'+el._tag+u'>'

    if el._tail:
        s += el._tail

    return s

cdef inline unicode _post(unicode s):
    return u'<!DOCTYPE html>'+s.replace(u'&lt;', u'<').replace(u'&gt;', u'>').replace(u'&amp;', u'&')

cdef inline Element _copy(Element orig):
    cdef Element orig_child, child

    cdef Element el = Element()
    el.tag = copy(orig.tag)
    el.text = copy(orig.text)
    el.tail = copy(orig.tail)
    #el.attrib = orig.attrib.copy()
    el.attrib = copy(orig.attrib)
    for orig_child in orig.children:
        child = _copy(orig_child)
        child.parent = el
        el.children.append(child)
    return el


cdef class Element:
    cdef Element _parent
    cdef list _children
    cdef unicode _tag
    cdef unicode _text
    cdef unicode _tail
    #cdef dict _attrib
    cdef list _attrib

    def __cinit__(self):
        #self._attrib = {}
        self._attrib = []
        self._children = []

    def __copy__(self):
        return _copy(self)

    cdef findall(self, unicode s):
        cdef list result = []
        _findall(self, s, result)
        return result

    def tostring(self):
        return u'<!DOCTYPE html>' + _tostring(self)

    property attrib:
        def __get__(self):
            return self._attrib

        #def __set__(self, dict attrib):
        def __set__(self, list attrib):
            self._attrib = attrib

    property tag:
        def __get__(self):
            return self._tag

        def __set__(self, unicode tag):
            self._tag = tag

    property text:
        def __get__(self):
            return self._text

        def __set__(self, unicode text):
            self._text = text

    property tail:
        def __get__(self):
            return self._tail

        def __set__(self, unicode tail):
            self._tail = tail

    property parent:
        def __get__(self):
            return self._parent

        def __set__(self, Element parent):
            self._parent = parent

    property children:
        def __get__(self):
            return self._children

        def __set__(self, list children):
            self._children = children


cdef Element SubElement(Element parent, unicode tag):
    cdef Element el = Element()
    el.tag = tag
    el.parent = parent
    parent.children.append(el)
    return el


cdef Element SubElementByIndex(Element parent, unicode tag, int index):
    cdef Element el = Element()
    el.tag = tag
    el.parent = parent
    parent.children.insert(index, el)
    return el


cdef _doc_py(Element r, long py_id, dict py_parse):
    cdef list py_list = r.findall(u'_py_')
    cdef Element e
    cdef Element p
    cdef unicode t
    cdef unicode k

    for e in py_list:
        t = e.text[1:-1]
        k = u'{0}_{1}'.format(py_id, t)
        o = py_parse[k]
        if isinstance(o, (list, tuple)):
            p = e.parent
            index = None
            if len(p.children) != 0:
                index = p.children.index(e)
            p.children.remove(e)
            _build_from_parent(p, index, map(unicode, o))
        else:
            _build_element(e, unicode(o))

def doc_py(r, py_id, py_parse):
    _doc_py(r, py_id, py_parse)

def doc_pre(f):
    return _doc_pre(f)

cdef Element _doc_pre(list f):
    cdef Element root, el, e

    root = Element()
    root.tag = u'root'
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
                is_super = 0
                for i, t in enumerate(attr):
                    if t[0] == u'super':
                        is_super = 1
                        attr.pop(i)
                        break
                if is_super:
                    e.children = []
                    #for child in e.children:
                    #    e.children.remove(child)
                #if attr.pop(u'super', None) is None:
                #    for child in e.children:
                #        e.children.remove(child)
            else:
                e = SubElement(root, _tag or u'div')
        elif ws > prev:
            e = SubElement(r[prev], _tag or u'div')
        elif ws == prev:
            e = SubElement(r[prev].parent, _tag or u'div')
        elif ws < prev:
            e = SubElement(r[ws].parent, _tag or u'div')
            
            for _ws in r.keys():
                if _ws > ws:
                    r.pop(_ws)
        
        e.text = text
        if _id:
            #e.attrib[u'id'] = _id
            e.attrib.append((u'id', _id))
            _ids[_id] = e
        if _class:
            #e.attrib[u'class'] = _class
            e.attrib.append((u'class', _class))
        if attr:
            #e.attrib.update(attr)
            e.attrib.extend(attr)
        
        r[ws] = e
        prev = ws
    
    if len(root.children) is 0:
        return None

    return root.children[0]

def _build_element(e, line):
    ws, l = _parse_ws(line)
        
    u, attr = _parse_attr(l)
    hash, text = _split_space(u)
    _tag, _id, _class = _parse_tag(hash)
    
    e.tag = _tag or u'div'
    e.text = text
    if _id:
        #e.attrib[u'id'] = _id
        e.attrib.append((u'id', _id))
    if _class:
        #e.attrib[u'class'] = _class
        e.attrib.append((u'class', _class))
    if attr:
        #e.attrib.update(attr)
        e.attrib.extend(attr)

def _build_from_parent(p, index, f):
    r = {'root': p}
    prev = ''
    plntxt = {}

    #from time import time
    #ws_time = 0
    #plntxt_time = 0
    #tag_time = 0
    #el_time = 0
    #attrib_time = 0

    cache = {}
    
    for line in f:
        #st = time()
        ws, l = _parse_ws(line)
        #ws_time += time()-st

        ### plntxt queue
        #st = time()
        if l[0] == u'\\':
            if ws in plntxt:
                plntxt[ws].append(l[1:])
            else:
                plntxt[ws] = [l[1:]]
            continue
        if plntxt:
            for _ws, text in plntxt.items():
                text = u' '+u' '.join(text)
                el = r[prev]
                if _ws > prev:
                    el.text += text
                else: # _ws == prev
                    el.tail = el.tail and el.tail+text or text
            plntxt = {}
        #plntxt_time += time()-st
        ###
        
        #st = time()
        if cache.has_key(l):
            _tag, _id, _class, attr, text = cache[l]
        else:
            #4.5   
            u, attr = _parse_attr(l)
            #0.8
            hash, text = _split_space(u)
            #7.7
            _tag, _id, _class = _parse_tag(hash)
            #13
            cache[l] = (_tag, _id, _class, attr, text)
        #tag_time += time()-st
        
        #st = time()
        if ws == u'':
            _p = None
            if index is not None:
                e = SubElementByIndex(p, _tag or u'div', index)
                index += 1
            else:
                e = SubElement(p, _tag or u'div')
        elif ws > prev:
            _p = r[prev]
            e = SubElement(_p, _tag or u'div')
        elif ws == prev:
            _p = r[prev].parent
            e = SubElement(_p, _tag or u'div')
        elif ws < prev:
            _p = r[ws].parent
            e = SubElement(_p, _tag or u'div')
            
            for _ws in r.keys():
                if _ws > ws:
                    r.pop(_ws)
        
        #el_time += time()-st
        
        #st = time()
        # fctr 5
        e.text = text
        if _id:
            #e.attrib[u'id'] = _id
            e.attrib.append((u'id', _id))
        if _class:
            #e.attrib[u'class'] = _class
            e.attrib.append((u'class', _class))
        if attr:
            #e.attrib.update(attr)
            e.attrib.extend(attr)
        # fctr 1
        r[ws] = e
        # fctr 1.5
        prev = ws
        #attrib_time += time()-st
    #print '!!!!!'
    #print 'ws_time: %.2f ms' % (ws_time*1000)
    #print 'plntxt_time: %.2f ms' % (plntxt_time*1000)
    #print 'tag_time: %.2f ms' % (tag_time*1000)
    #print 'el_time: %.2f ms' % (el_time*1000)
    #print 'attrib_time: %.2f ms' % (attrib_time*1000)
    #print '!!!!!'


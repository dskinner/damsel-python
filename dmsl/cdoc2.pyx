from _cutils cimport _parse_ws, _parse_attr, _parse_tag, _split_space

cdef class Element:
    cdef Element _parent
    cdef list children
    cdef unicode _tag
    cdef unicode _text
    cdef unicode _tail
    cdef dict _attrib

    def set_text(self, unicode text):
        self.text = text

    def get_text(self): return self.text
    def get_tag(self): return self.tag
    def get_children(self): return self.children
    def get_parent(self): return self._parent
    
    def __cinit__(self):
        self.children = []

    def _to_string(self):
        result = ['<', self.tag]

        for k, v in self.attrib.items():
            result.extend([' ', k, '="', v, '"'])
        
        result.extend(['>', self.text])

        for child in self.children:
            result.extend(child._to_string())

        result.extend(['</', self.tag, '>'])

        if self.tail:
            result.append(self.tail)

        return result

    def to_string(self):
        '''
        result = []
        result.extend(['<', self.tag])
        for k, v in self.attrib.items():
            result.extend([' ', k, '="', v, '"'])
        result.extend(['>', self.text])
        if len(self.children) != 0:
            for child in self.children:
                result.append(child.to_string())
        result.extend(['</', self.tag, '>'])
        if self.tail:
            result.append(self.tail)
        return ''.join(result)
        '''
        return ''.join(self._to_string())

    def findall(self, unicode s):
        cdef list result = []

        def _findall(Element el, unicode srch, list result):
            for child in el.get_children():
                if child.get_tag() == srch:
                    result.append(child)
                if len(child.get_children()) != 0:
                    _findall(child, srch, result)
        _findall(self, s, result)
        return result
    
    property attrib:
        def __get__(self):
            if not self._attrib:
                self._attrib = {}
            return self._attrib
    
    property tag:
        def __get__(self):
            return self._tag
        def __set__(self, unicode tag):
            self._tag = tag

    property text:
        def __get__(self):
            if not self._text:
                self._text = u''
            return self._text
        def __set__(self, unicode text):
            self._text = text

    property tail:
        def __get__(self):
            if not self._tail:
                return False
            return self._tail
        def __set__(self, unicode tail):
            self._tail = tail

    property parent:
        def __get__(self):
            return self._parent

        def __set__(self, Element parent):
            self._parent = parent
            #self._parent.children.append(self)

cdef Element SubElement(Element parent, unicode tag):
    cdef Element el = Element()
    el.tag = tag
    el.parent = parent
    el.parent.get_children().append(el)
    return el

cdef Element SubElementByIndex(Element parent, unicode tag, int index):
    cdef Element el = Element()
    el.tag = tag
    el.parent = parent
    el.parent.get_children().insert(index, el)
    return el

cdef _doc_py(Element r, long py_id, dict py_parse):
    cdef list py_list = r.findall(u'_py_')
    cdef Element e
    cdef Element p
    cdef unicode t
    cdef unicode k
    
    for e in py_list:
        t = e.get_text()[1:-1]
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
                if attr.pop('super', None) is None:
                    for child in e.children:
                        e.children.remove(child)
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
        
        e.set_text(text)
        if _id:
            e.attrib['id'] = _id
            _ids[_id] = e
        if _class:
            e.attrib['class'] = _class
        if attr:
            e.attrib.update(attr)
        
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
    #from time import time
    #ws_time = 0
    #plntxt_time = 0
    #tag_time = 0
    #el_time = 0
    #attrib_time = 0
    
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
                text = ' '+' '.join(text)
                el = r[prev]
                if _ws > prev:
                    el.text += text
                else: # _ws == prev
                    el.tail = el.tail and el.tail+text or text
            plntxt = {}
        #plntxt_time += time()-st
        ###
        
        #st = time()
        u, attr = _parse_attr(l)
        hash, text = _split_space(u)
        _tag, _id, _class = _parse_tag(hash)
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
            _p = r[prev].get_parent()
            e = SubElement(_p, _tag or u'div')
        elif ws < prev:
            _p = r[ws].get_parent()
            e = SubElement(_p, _tag or u'div')
            
            for _ws in r.keys():
                if _ws > ws:
                    r.pop(_ws)
        
        #el_time += time()-st
        
        #st = time()
        # fctr 7
        #if index is not None and _p is None:
        #    p.get_children().remove(e)
        #    p.get_children().insert(index, e)
        #    index += 1
        #st = time()
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
        #attrib_time += time()-st
    #print '!!!!!'
    #print 'ws_time: %.2f ms' % (ws_time*1000)
    #print 'plntxt_time: %.2f ms' % (plntxt_time*1000)
    #print 'tag_time: %.2f ms' % (tag_time*1000)
    #print 'el_time: %.2f ms' % (el_time*1000)
    #print 'attrib_time: %.2f ms' % (attrib_time*1000)
    #print '!!!!!'


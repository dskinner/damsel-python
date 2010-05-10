#! /usr/bin/env python
# -*- coding: utf-8 -*-
#from lxml.etree import Element
from _element import Element
from collections import deque

def _doc_parse(f):
    r = []
    plntxt = deque()

    for line in f:
        line = line.rstrip()
        l = line.lstrip()
        ws = line[:-len(l)]
        
        if l[0] == '%':
            l = l[1:]
        elif l[0] == '#':
            #l = l.replace('#', '%#', 1)
            pass
        elif l[0] == '.':
            #l = l.replace('.', '%.', 1)
            pass
        elif l[0] == "\\":
            plntxt.append((ws, l.replace('\\', '', 1)))
            continue
        else:
            plntxt.append((ws, l))
            continue


        # check plntxt queue
        # everything in queue should be same indention width
        # since nowhere in a doc should there be plain text indented to plain text
        #for x in plntxt:
        while plntxt:
            ws, text = plntxt.popleft()
            j = -1
            while j:
                if ws > r[j][0]:
                    r[j][1].text += ' '+text
                    break
                elif ws == r[j][0]:
                    if r[j][1].tail is None: # faster than init'ing tail on element creation everytime
                        r[j][1].tail = text
                    else:
                        r[j][1].tail += ' '+text
                    break
                j -= 1

        #l = l.partition('%') # ('    ', '%', 'tag#id.class(attr=val) content')

        # determine tag attributes
        attr = None
        if '(' in l:
            op_i = l.index('(')
            if ' ' not in l[:op_i]: # there should be no spaces in %tag#id.class(...
                cp_i = l.index(')')+1
                attr = l[op_i:cp_i]
                u = l.replace(attr, '').partition(' ')
            else:
                u = l.partition(' ')
        else:
            u = l.partition(' ')


        # this is pretty sweet, basically it will always return the following format
        #   [('tag', '', 'class'), ('#', '', ''), ('id', '.', 'class')]
        # no matter the string order of elements, for example
        #   tag#id.class.class
        #   tag.class#id.class
        #   tag.class.class#id
        #   #id.class.class
        #   #id
        # for all of these examples, tag will always be [0][0], id will always be [2][0]
        # and class will always be [0][2]+[2][2]
        # and this should be effin fast comparitively (to regex, other builtin string operations)
        tag = [x.partition('.') for x in u[0].partition('#')]

        #
        e = Element(tag[0][0] or 'div')
        e.text = u[2]

        if tag[2][0] != '':
            e.attrib['id'] = tag[2][0]

        # TODO is this the fastest way to process classes and attributes?
        _class = tag[0][2] + ' ' + tag[2][2]
        if _class != ' ':
            e.attrib['class'] = _class.replace('.', ' ').strip()

        if attr is not None:
            for x in attr[1:-1].split(','):
                k, tmp, v = x.partition('=')
                e.attrib[k.strip()] = v.strip()

        r.append((ws, e)) # ('    ', etree.Element)
    return r


if __name__ == '__main__':
    from _pre_parse import _pre_parse
    from _py_parse import _py_parse
    import sys
    from time import time

    _f = sys.argv[1]
    _f = open(_f).readlines()
    t = sys.argv[2]

    if t == 'y':
        times = []
        for x in range(2000):
            a = time()
            f = _pre_parse(_f)
            f = _py_parse(f)
            f = _doc_parse(f)
            times.append(time()-a)
        print min(times)
    else:
        f = _pre_parse(_f)
        f = _py_parse(f)
        f = _doc_parse(f)

        for x in f:
            print `x`


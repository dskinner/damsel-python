# -*- coding: utf-8 -*-
from lxml import etree
from collections import deque

def parse_doc(f):
    r = []
    plntxt = deque()

    for l in f:
        l = l.rstrip() # remove line break endings
        if l == '': # ditch this in preprocessor?
            continue

        # inspect directive, determine if plain text
        d = l.lstrip()
        directive = d[0]
        if directive == '%':
            pass
        elif directive == '#':
            l = l.replace('#', '%#', 1)
        elif directive == '.':
            l = l.replace('.', '%.', 1)
        elif directive == "\\":
            ws = l.partition('\\')[0]
            plntxt.append((d.replace('\\', '', 1), ws))
            continue
        else:
            #ws = l.partition(directive)[0]
            ws = l[:-len(d)]
            #print `ws`
            plntxt.append((d, ws))
            continue


        # check plntxt queue
        # everything in queue should be same indention width
        # since nowhere in a doc should there be plain text indented to plain text
        #for x in plntxt:
        while plntxt:
            text, ws = plntxt.popleft()
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

        l = l.partition('%') # ('    ', '%', 'tag#id.class(attr=val) content')

        # determine tag attributes
        attr = None
        if '(' in l[2]:
            op_i = l[2].index('(')
            if ' ' not in l[2][:op_i]: # there should be no spaces in %tag#id.class(...
                cp_i = l[2].index(')')+1
                attr = l[2][op_i:cp_i]
                u = l[2].replace(attr, '').partition(' ')
            else:
                u = l[2].partition(' ')
        else:
            u = l[2].partition(' ')


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
        e = etree.Element(tag[0][0] or 'div')
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

        r.append((l[0], e)) # ('    ', etree.Element)
    return r

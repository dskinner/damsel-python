#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
FEATURES TO IMPLEMENT
---------------------
* static html instead of quick tags
* line escaping for text using \
* attribute syntax (attr=val) can stretch multiple lines
  this one can be done by seeing it doesn't end, buffer it,
  and mark the next iteration a continuation, maybe?
* be able to call python functions?
* tag/ self closing tags? does it matter? lxml etree handling this
* whitespace control with > and < does this matter? relevant? etree again
  handling pre elements could be trouble and relevant
* declare a doctype at top of document and charset, pass on to etree.tostring
* forward slash / for html comments, or how about just writing html comments...
  hmm but wrapping indented sections of code, now we're talkin
* /[if IE] oh yeah, need this
* comments specific to the doc that are not rendered anywhere, and indented
  sections are included as part of the comment
* a python eval declartion using =
* hyphen to run python? something like
  - for x in range(4)
      %p x
  and then an unindent would end this bit
* whitespace preservation?
* :javascript directive? using colon to have filters where text would get passed
  to a function? seems a bit redundant but nice syntax, maybe theres a middle ground
* wtf is interpolation all about?
* escaping/unescaping html
* pass namespace of controller method to formatter, that would kick fucking ass
  @publisher
  def index(self):
      cat = 'meow'
  ---
  %p {cat}
  ---
  but this could get funky, request data in json? pick up trash locals? i dunno
"""

from lxml import etree
from time import time
import re

p2 = re.compile('(\(.*?\))') # pull out attribute declarations

#process_plntxt()
# FIXME process_plntxt after parse "for-loop" finishes for plain text located
# at the end of document

def parse(f):
    r = []
    plntxt = []
    
    for l in f.splitlines(): # enumerate for '%' check FIXME better way? save 0.1ms
        # skip blank lines, just saved 0.4ms doing it this way!
        t = l.rstrip()
        if t == '':
            continue

        # no directive (%)? append to plntxt and skip
        if '%' not in t:
            plntxt.append(t)
            continue

        # check plntxt queue
        if len(plntxt) is not 0:
            for x in plntxt:
                text = x.strip()
                ws = ' '*(len(x)-len(text))
                j = -1
                while j:
                    if ws > r[j][0]:
                        if r[j][1].text is None:
                            r[j][1].text = text
                        else:
                            r[j][1].text += ' '+text
                        break
                    elif ws == r[j][0]:
                        if r[j][1].tail is None:
                            r[j][1].tail = text
                        else:
                            r[j][1].tail += ' '+text
                        break
                    j -= 1
            plntxt = []
            
        ###
        
        t = t.partition('%') # ('    ', '%', 'tag#id.class(attr=val) content')
        
        attr = None
        if '(' in t[2]:
            # FIXME content with parenthesis but tag without attributes will go wrong
            # TODO can this be done without regex? save 0.3ms
            rsplt = p2.split(t[2])              # ['tag#id.class', '(attr=val)', 'content ', '(with)', ' parenthesis']
            attr = rsplt.pop(1)                 # returns '(attr=val)'
            
            u = ''.join(rsplt).partition(' ')   # ('tag#id.class', ' ', 'content (with) parenthesis')
        else:
            u = t[2].partition(' ')             # ('tag#id.class', ' ', 'content')

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
        
        name = tag[0][0] != '' and tag[0][0] or 'div'
        #print '@@@:', tag
        e = etree.Element(name)
        # FIXME slow slow slow slow slow...
        # FIXME splitting attributes with ', ' but it could be so many other ways like ',' or ',  ' or ' , '
        if attr is not None:
            for x in attr[1:-1].split(', '):
                k, v = x.split('=')
                e.attrib[k] = v
        e.text = u[2]
        if tag[2][0] != '':
            e.attrib['id'] = tag[2][0]

        _class = tag[0][2] + ' ' + tag[2][2]
        if _class != ' ':
            e.attrib['class'] = _class.replace('.', ' ').strip()

        r.append((t[0], e))
    return r


def heuristic_test(parsed):
    """
    This returns a step-count based on indention. The step-count represents
    the number of steps upward an element needs to move to find its parent.
    This is only accurate for counts of more and same. Less can not be divined
    """
    m = []
    more = 0
    same = 0

    prev = parsed[0][0]
    for d in parsed[1:]:
        if d[0] > prev:
            m.append(1)
            more += 1
            same = 0
        elif d[0] == prev:
            m.append(2+same) # (m->s) == 2
            same += 1
        elif d[0] < prev:
            m.append(more+same+1)
            more = 0
            same = 0
        prev = d[0]
    return m

def hr_build(parsed):
    """
    This combines the heuristic and relative build methods. The heuristic method
    is able to figure out position of positively indented elements faster but is unable to
    tell position when indention decreases. At this point, we use a relative position
    method to locate this node's parent. The speed increase is minimal, but every bit helps.
    
    When a section unindents, I think its safe to assume that it will fall on a pre-existing
    indention level. All this is hardly my forte so this may be wrong. By recording a map of
    all the latest elements on an indention level, we can access the last element on the same
    indention level, get its parent, and append the new element to it. The one catch with this
    method is we need to remove any mappings to larger indentions of the current unindent so
    future elements do not get appended to incorrect items if variable indention is used.
    """
    r = parsed
    more = 0
    same = 0
    m = {}

    prev = parsed[0][0]
    for i, d in enumerate(parsed[1:]):
        i += 1
        if d[0] > prev:
            r[i-1][1].append(r[i][1])   # ('    ', Element)[1].append(...)
            more += 1
            same = 0
            m[d[0]] = i         # m['    '] = 1
        elif d[0] == prev:
            r[i-(2+same)][1].append(r[i][1])    # (more_indent->same_indent) == 2
            same += 1
        elif d[0] < prev:
            j = m[d[0]]     # j = [i]
            m[d[0]] = i         # m['    '] = 1
            #print etree.tostring(r[0][1])
            parent = r[j][1].getparent()
            parent.append(d[1])
            
            # clear step counts
            more = 0
            same = 0

            # purge mapping of larger indents then this unindent
            for k in m.keys():
                if k > d[0]:
                    m.pop(k)
            
        prev = d[0]
    return r


def relative_build(parsed):
    """
    stable parsing of document, but slightly slower then heuristic (which is still questionable atm)
    """
    r = [x for x in parsed if not isinstance(x, str)]
    m = {}
    prev = parsed[0][0]
    for i, d in enumerate(parsed[1:]):
        i += 1
        k, v = d
        if k in m:
            j = m[k]
            parent = r[j][1].getparent()
            child = r[i][1]
            parent.append(child)
            m[k] = i
        else:
            m[k] = i
            parent = r[i-1][1]
            child = r[i][1]
            parent.append(child)
        if d[0] < prev:
            for k in m.keys():
                if k > d[0]:
                    m.pop(k)
        prev = d[0]
    return r



###################################


def haml(f='test.hdae', t='r'):
    _f = open(f).read()
    l = parse(_f)
    if t == 'r':
        b = relative_build(l)
    elif t == 'hr':
        b = hr_build(l)
    elif t == 'h':
        b = heuristic_test(l)
    return b[0][1]

if __name__ == '__main__':
    import sys
    f = sys.argv[1]
    t = sys.argv[2]
    if t == 'r':
        test = relative_build
    if t == 'hr':
        test = hr_build
    if t == 'haml':
        print etree.tostring(haml(f))
        sys.exit()
    
    times = []
    for x in range(20):
        a = time()
        _f = open(f).read()
        l = parse(_f)
        test(l)
        times.append(time()-a)
    print min(times)

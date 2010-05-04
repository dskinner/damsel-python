#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
FEATURES TO IMPLEMENT
---------------------
* colon directive multiline wrapping
  :myfunc
      some param
      and more
  which would be the equivalent of calling
  :myfunc('some param\nandmore')
* setup string.Formatter custom namespace instead of
  passing in locals that actually isn't slow..
* reserve keywords for safe_locals such as "encoding", "doctype", etc,
  and make it known in coming documentation
* declare a doctype at top of document and charset, pass on to etree.tostring
* FIXME need to create a safe way to open files with :include()
* static html instead of quick tags
* line escaping for text using \
* attribute syntax (attr=val) can stretch multiple lines
  implement in preprocessor?
* evaluate the NEED for a preprocessor..
  
IDEAS
-----
* tag/ self closing tags? does it matter? lxml etree handling this
* whitespace control with > and < does this matter? relevant? etree again
  handling pre elements could be trouble and relevant
* forward slash / for html comments, or how about just writing html comments...
  hmm but wrapping indented sections of code, now we're talkin
* /[if IE] oh yeah, need this
* comments specific to the doc that are not rendered anywhere, and indented
  sections are included as part of the comment
* not sure how best to handle this,
  :for x in range(3):
      %p {x}
* whitespace preservation?
* :javascript directive?
* escaping/unescaping html
* pass namespace of controller method to formatter, that would kick fucking ass
  @publisher(_locals=True)
  def index(self):
      cat = 'meow'
  ---
  %p {cat}
  ---
* conditionals inside of attribute tags (attr=val) somehow something nice.. would probably
  fit in with - for syntax
  :r = range(4)
  - for i in r
      %li({if i+1 == len(r): class=last}) i
  I've never liked looking at code like this, maybe something more appropriate that already is functional
  is embedding functions inline
  :r = range(4)
  :is_last = lambda x: len(r) == x+1 and 'class="last"' or ''
  :for i, x in enumerate(r):
      %p(attr=val,:is_last(i)) {x}
  of course the plain text indent doesn't work yet..

BUGFIXES
--------
look for the fixme's atm
FIXME process_plntxt after parse "for-loop" finishes for plain text located

"""
import __builtin__
from lxml import etree
from time import time
from string import Formatter
import sys

fmt = Formatter()

def include(f):
    _f = open(f).readlines()
    _f = parse_py(_f)
    return _f

def block(s):
    s = s.splitlines()
    s = parse_py(s)
    safe_globals['__blocks__'][s[0]] = [s[1:], False] # [content, been-used-yet?]
    return

def safe_eval(s):
    return eval(s, safe_globals)

def to_local(i, l):
    return '''globals()["""__{0}_{1}__"""]={1}'''.format(i, l)

def parse_call(i, l):
    if l[-1] == ':': # def, if, for; code block
        return l
    if l[0] == ' ': # a continued code block
        return l
    
    if '(' in l:
        a = l.index('(')
    else:
        return l
    if '=' in l:
        b = l.index('=')
    else:
        return to_local(i, l)
    if a < b:
        return to_local(i, l)
    else:
        return l

def parse_py(f):
    """
    FIXME I hacked this code to hell the other day, fix it, refactor it, make
    it beautiful again. Run speed tests, get it back close to what it was.
    Identify those bottle-necks and find a better way.
    """
    
    queue = []
    for i, l in enumerate(f):
        l = l.strip()
        if l == '':
            continue

        # see if this is :directive line
        directive = l[0]
        if directive == ':':
            queue.append((i, l, parse_call(i, l[1:])))
            continue

        # check if {variable} is embedded in line
        if '{' in l: # TODO and '}' in l
            for x in fmt.parse(l):
                if x[1] is not None:
                    queue.append((i, x[1], to_local(i, x[1])))

        # look to see if :directive is embedded in line
        if ':' in l:
            a = l.index(':')
        else:
            continue
        if '(' in l:
            b = l.index('(')
        else:
            continue
        if ' ' in l[a:b]:
            continue
        c = l.index(')')+1
        queue.append((i, l[a:c], to_local(i, l[a+1:c])))

    cmd_s = '\n'.join([x[2] for x in queue])
    #print cmd_s
    c = compile(cmd_s, '<string>', 'exec')
    safe_eval(c)
        
    ###
    offset = 0
    for e in queue:
        i = e[0]
        l = e[1]
        
        if l[0] != ':':
            k = '''__{0}_{1}__'''.format(i, l)
            l = '{'+l+'}'
        else:
            k = '''__{0}_{1}__'''.format(i, l[1:])

        if k in safe_globals:
            v = safe_globals[k]
            if isinstance(v, (list, tuple)): # if iterable, then indent everything appropriately
                indention = f[i+offset].replace(l, '', 1).rstrip('\r\n')
                f.pop(i+offset)
                offset -= 1
                for x in v:
                    offset += 1
                    f.insert(i+offset, indention+str(x)) # FIXME str() get around this?
            else:
                i += offset
                f[i] = f[i].replace(l, v, 1)
        elif ':block(' == e[1].lstrip()[:7]: # was this a block?
            # FIXME for the love of god, fixme!
            n = `e[1]`.split('\\n')[0].split('\\')[0].split("'")[1]
            v, u = safe_globals['__blocks__'][n]
            if u:
                i += offset
                f[i] = f[i].replace(l, '', 1)
                continue
            indention = f[i+offset].replace(l, '', 1).rstrip('\r\n')
            f.pop(i+offset)
            offset -= 1
            for x in v:
                offset += 1
                f.insert(i+offset, indention+x)
            safe_globals['__blocks__'][n][1] = True
        else:
            i += offset
            f[i] = f[i].replace(l, '', 1)

    return f

def parse_doc(f):
    r = []
    plntxt = []

    for l in f:
        l = l.rstrip() # remove line break endings
        if l == '':
            continue # skip blank lines

        # inspect directive, determine if plain text
        d = l.lstrip()
        directive = d[0]
        if directive == '%':
            pass
        elif directive == '#':
            l = l.replace('#', '%#', 1)
        elif directive == '.':
            l = l.replace('.', '%.', 1)
        elif directive == "'" and d[:3] == "'''":
            continue # TODO mark comment start and do continues till end found
        #elif directive == ':':
        #    output = inline_eval(d[1:])
        #    if output is None:
        #        continue
        #    l = l.replace(d, output)
        else:
            plntxt.append(l)
            continue

        
        # check plntxt queue
        # everything in queue should be same indention width
        # since nowhere in a doc should there be plain text indented to plain text
        for x in plntxt:
            text = x.strip()
            ws = ' '*(len(x)-len(text))
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
            
        plntxt = []
        
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
                k, v = x.split('=')
                e.attrib[k.strip()] = v.strip()
        
        r.append((l[0], e)) # ('    ', etree.Element)
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
    As tags indent, it is easy to identify the parent. It is simply the last
    element processed. If indention is the same, it is simply the last elements
    parent.

    While processing this data, we can record a dict indexed by indention. When
    a tag decreases in indention, I think it is safe to assume that it will
    fall on a pre-existing indention level. This will trigger a lookup in the
    dict and get the parent of that element. Afterwards, we clean up the dict
    to remove all keys with an indention level higher then the decreased one so
    future elements do not get appended to incorrect items if variable
    indention is used.
    """
    r = parsed
    more = 0
    same = 0
    m = {}

    prev = parsed[0][0]
    for i, d in enumerate(parsed):
        if i is 0:
            continue
        
        ws = d[0]
        
        if ws > prev:
            r[i-1][1].append(r[i][1])   # ('    ', Element)[1].append(...)
            m[ws] = i
        elif ws == prev:
            r[i-1][1].getparent().append(r[i][1])
            m[ws] = i
        elif ws < prev:
            j = m[ws]
            r[j][1].getparent().append(r[i][1])
            # purge mapping of larger indents then this unindent
            for k in m.keys():
                if k > ws:
                    m.pop(k)
            m[ws] = i
        prev = ws
    return r

def relative_build(parsed):
    """
    Stable parsing of document, but slightly slower then hr_build which should
    should be stable now too.
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

safe_locals = {}

safe_globals = {'__builtins__': None,
                '__blocks__': {},
                'dict': __builtin__.dict,
                'enumerate': __builtin__.enumerate,
                'globals': __builtin__.globals,
                'len': __builtin__.len,
                'list': __builtin__.list,
                'locals': __builtin__.locals,
                'open': __builtin__.open, # FIXME make a safe wrapper for opening additional theme files safely
                'map': __builtin__.map,
                'min': __builtin__.min,
                'max': __builtin__.max,
                'range': __builtin__.range,
                'block': block,
                'title': "SIMLE",
                'include': include,
                'parse_py': parse_py}


def parse_preprocessor(f):
    """
    The intention of this is to clean up and format the document before being
    handed to parse_py. This is to allow for a non-pythonic syntax in the
    document that makes sense for formatting text but still leverages python
    to easily process the filter. It is also intended to clean up any other
    short-cuts or features in the document before it gets handed to parse_doc
    such as multiline breaks of tag attributes.

    TODO Due to the nature of this, it might be best implemented with regex
    over the course of the whole document. Perform various speed tests to see
    what works fastest.
    
    TODO setup attributes to span multiple lines
    """
    _f = f
    offset = 0
    for i, x in enumerate(_f):
        if x[:9] == ':extends(':
            nf = open(x.split("'")[1]).readlines()
            nf = parse_preprocessor(nf) # for multi-depth :extends(...)
            f.pop(i+offset)
            offset -= 1
            for y in nf:
                offset += 1
                f.insert(i+offset, y)
                
    return f


###################################

def parse(f, t='hr'):
    # process eval stuff first
    f = parse_preprocessor(f)
    f = parse_py(f)
    
    #parse document next
    l = parse_doc(f)
    if t == 'r':
        b = relative_build(l)
    elif t == 'hr':
        b = hr_build(l)
    elif t == 'h':
        b = heuristic_test(l)
    return etree.tostring(b[0][1])

def test(func):
    from time import time
    times = []
    for x in range(20):
        a = time()
        func()
        times.append(time()-a)
    print(min(times))


if __name__ == '__main__':
    import sys
    f = sys.argv[1]
    t = sys.argv[2]

    f = open(f).readlines()
    
    def render(f, t):
        def _render():
            return parse(f, t)
        return _render
    
    if t == 'r':
        test(render(f, t))
    if t == 'hr':
        test(render(f, t))
    if t == 'daml':
        print parse(f)


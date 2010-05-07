#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
FEATURES TO IMPLEMENT
---------------------
* Looking over django-mako to get an idea of whats involved with plugging into
  django. Looks like theres all kinds of crazy tidbits to read up on. I would
  prefer this to be able to replace any/all current functionality in
  django-templates while also providing the option to be flexible and go
  back and forth. If I write anything to plug this into django, I want it to
  be complete.
* TODO replace all split()s with partition()
* setup string.Formatter custom namespace
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

FIXMEH's
--------
look for the fixme's atm
FIXME process_plntxt after parse "for-loop" finishes for plain text located
FIXME im sure theres erroneous errors related to ' " in the code everywhere
    create unit tests and find the problems if they are there

"""
try:
    import __builtin__
except ImportError:
    import builtins as __builtin__ #Python 3.0

from lxml import etree
from time import time
from string import Formatter
import sys
import os.path

class LXML(object):
    """
    Used to declare lxml.etree.tostring params by declaring attributes. This
    ends up working faster then declaring variables and scraping and is easier
    on the eyes and fingers for declaring common tostring keyword arguments
    versus the use of a traditional dict.
    """
    pass

fmt = Formatter()

template_dir = ''

def safe_open(f):
    """
    There doesn't appear to be a need to check for an escaped string sequence
    such as .\.\/ or any variant as none of pythons os methods appears to
    recognize this. TODO Check other template frameworks to see how this is
    handled.

    TODO See about a relative import based on main file's location, so
    specifying a path of /template.daml would be an absolute path where root
    is the template_dir and template.daml would be relative to whatever daml
    file referenced it (include, extends, etc).
    """
    if '../' in f:
        raise Exeception()
    
    return open(os.path.join(template_dir, f))

def safe(s):
    """
    do not escape html contained here
    """
    _s = parse_py(s.splitlines(), esc=False)
    return _s

def include(f):
    _f = safe_open(f).readlines()
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
    # i should rethink this, it can lead to trouble down the road
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

def escape(s):
    """
    This will escape html output. This will get escaped a second time on
    document output and be represented as &amp;gt; and &amp;lt; respectively.
    The post processor will transform all &gt;'s and &lt;'s first and then
    transform all &amp;'s to keep responses sanitized.
    """
    return s.replace('>', '&gt;').replace('<', '&lt;')

def parse_py(f, esc=True):
    """
    """
    
    queue = []
    for i, l in enumerate(f):
        l = l.strip()
        if l == '':
            continue

        # see if this is :directive line
        directive = l[0]
        if directive == '\\':
            continue
        if directive == ':':
            queue.append((i, l, parse_call(i, l[1:])))
            continue

        # check if {variable} is embedded in line
        if '{' in l: # TODO get string.formatter working correctly
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
        if ' ' in l[a:b] or a > b: # check a>b for attributes that have :
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
                    if esc:
                        x = escape(x)
                    offset += 1
                    f.insert(i+offset, indention+str(x)) # FIXME str() get around this?
            else:
                if esc:
                    v = escape(v)
                i += offset
                f[i] = f[i].replace(l, v, 1)
        # TODO setup a hooks system for template functions to hook into
        elif ':block(' == e[1].lstrip()[:7]: # was this a block?
            # FIXME for the love of god, fixme!
            #n = `e[1]`.split('\\n')[0].split('\\')[0].split("'")[1]
            n =  e[1].split("'")[1].split('\\')[0]
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
        elif directive == "\\":
            plntxt.append(l.replace('\\', '', 1))
            continue
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
                'open': safe_open, # FIXME make a safe wrapper for opening additional theme files safely
                'map': __builtin__.map,
                'min': __builtin__.min,
                'max': __builtin__.max,
                'range': __builtin__.range,
                'block': block,
                'include': include,
                'parse_py': parse_py,
                'safe': safe,
                'lxml': LXML()}

# Python3
if hasattr(__builtin__, 'False'):
    safe_globals['False'] = getattr(__builtin__, 'False')

if hasattr(__builtin__, 'True'):
    safe_globals['True'] = getattr(__builtin__, 'True')
#

def get_leading_whitespace(s):
    def _get():
        for x in s:
            if x != ' ':
                break
            yield x
    return ''.join(_get())

def parse_postprocessor(s):
    """
    For now, should look for html tags embedded in Element.text and
    Element.tail with some sort of marker that says to unescape this.
    This can be done after tostring maybe with a find/replace or it
    could be done before tostring and create proper Element's adjusting
    head/tail text and appending as necessary. Im guessing the latter
    would be slower.

    NOTE this cant be done post-processor after tostring, theres no way to
    know when something was marked safe.
    """
    return s.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')

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

    FIXME theres a subtle bug here that has to do with '\n'.join()s that
        causes havoc and headaches, look at
        :safe {menu}
        as an example. Didn't show up in :block since it establishes its
        place in the global namespace manually.
    """
    _f = f
    offset = 0

    multiline_func = None # [parent-indent, first-child-indent, parent-index, string-list]
    
    for i, x in enumerate(_f[:]):
        x = x.rstrip()
        if x == '':
            f.pop(i+offset)
            offset -= 1
            continue
        
        # check queue if we need to append this line
        if multiline_func is not None:
            #check indention and append appropriately
            ws = get_leading_whitespace(x) # should keep up with this data and never call this func again
            if ws > multiline_func[0]:
                f.pop(i+offset)
                offset -= 1
                if multiline_func[1] is None:
                    multiline_func[1] = ws
                multiline_func[3].append(x[len(multiline_func[1]):])
            else: # handle and clear queue once indention decreases to right place
                multiline_func[3].append("')\n")
                f.insert(multiline_func[2]+1, '\\n'.join(multiline_func[3])) #insert after, not before
                offset += 1
                multiline_func = None
        
        #
        d = x.lstrip()
        directive = d[0] # if i keep the preprocessor, stuff like this might be able to get saved for use by parser
        if directive == ':':
            if '(' not in d and '=' not in d:
                f.pop(i+offset)
                offset -= 1

                y = d.partition(' ')
                ws = x.partition(':')[0]
                
                multiline_func = [ \
                    ws,    # original whitespace
                    None,                   # first childs whitespace
                    i+offset,               # original index
                    [ws+y[0]+"('"+y[2]]]             # build string
                
                continue
            
            elif d[:9] == ':extends(': #factor this out, should only run at top of document, not every effin line
                nf = safe_open(x.split("'")[1]).readlines() # FIXME safe_open
                nf = parse_preprocessor(nf) # for multi-depth :extends(...)
                f.pop(i+offset)
                offset -= 1
                for y in nf:
                    offset += 1
                    f.insert(i+offset, y)
    
    if multiline_func is not None: # ugh, one last check, need better solution for this
        multiline_func[3].append("')\n")
        f.append('\\n'.join(multiline_func[3]))
    
    return f

def tostring(o):
    """
    """
    return etree.tostring(o, **safe_globals['lxml'].__dict__)
    

###################################
from copy import copy

def parse(f, t='hr', sandbox={}):
    global safe_globals
    _safe_globals = copy(safe_globals)
    safe_globals['lxml'] = LXML()
    safe_globals.update(sandbox)
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
    s = tostring(b[0][1])
    safe_globals = copy(_safe_globals)
    s = parse_postprocessor(s)
    return s

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

    f = safe_open(f).readlines()
    
    def render(f, t):
        def _render():
            return parse(f, t)
        return _render
    
    if t == 'r':
        test(render(f, t))
    if t == 'hr':
        test(render(f, t))
    if t == 'daml':
        print(parse(f))


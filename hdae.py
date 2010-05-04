#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
FEATURES TO IMPLEMENT
---------------------
* colon directive.
  :myfunc
      some param
      and more
  which would be the equivalent of calling
  :myfunc('some param\nandmore')
* setup string.Formatter custom namespace instead of
  passing in safe_locals
* try to speed up eval, check out mako source maybe?
  speed up eval by making only one eval call. Somehow get all
  : directives, viewing it as an overlay, remember where each
  directive is located, and produce a controlled result of all
  directives with a single eval call. Then layer this back into
  the original document. It's crazy, but it just might work...
  re.findall(':(.*\=.*$|.*\))', f, re.M)
* reserve keywords for safe_locals such as "encoding", "doctype", etc
* FIXME need to create a safe way to open files with :include()

IDEAS
-----
* static html instead of quick tags
* line escaping for text using \
* attribute syntax (attr=val) can stretch multiple lines
  this one can be done by seeing it doesn't end, buffer it,
  and mark the next iteration a continuation, maybe?
* tag/ self closing tags? does it matter? lxml etree handling this
* whitespace control with > and < does this matter? relevant? etree again
  handling pre elements could be trouble and relevant
* declare a doctype at top of document and charset, pass on to etree.tostring
* forward slash / for html comments, or how about just writing html comments...
  hmm but wrapping indented sections of code, now we're talkin
* /[if IE] oh yeah, need this
* comments specific to the doc that are not rendered anywhere, and indented
  sections are included as part of the comment
* not sure how best to handle this,
  - for x in range(4)
      %p x
  and then an unindent would end this bit
* whitespace preservation?
* :javascript directive?
  :overlay main.hdae namethis
  would process this document then create a dict(namethis=processed) passed to the formatter
  to overlay specified maybe? sounds good for one, but what about multiple includes?
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

def parse_args(l):
    """
    returns (args, kwargs)
    """
    a = []
    d = {}
    for x in l.split(','):
        if '=' in x:
            k, v = x.split('=')
            d[k.strip()] = v.strip()
        else:
            a.append(x.strip())
    return (a, d)

def process_internal(l):
    a = l.index(':')+1
    b = l.index('(')
    c = l[a:b]
    if c in extensions:
        args, kwargs = parse_args(l[b+1:-1])
        extensions[c](*args, **kwargs)

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

def is_func_call(l):
    if '(' in l:
        a = l.index('(')
    else:
        return False
    if '=' in l:
        b = l.index('=')
    else:
        return True
    if a < b:
        return True
    else:
        return False

def is_embedded(l):
    # look to see if :directive is embedded in line
    if ':' in l:
        a = l.index(':')
    if '(' in l:
        b = l.index('(')
    else:
        return False
    if ' ' in l[a:b]:
        return False
    c = l.index(')')+1
    return l[a+1:c]

def inline_eval(l):
    if is_func_call(l):
        return eval(l, {'__builtins__': None}, safe_globals)
    else:
        a, b = [x.strip() for x in l.split('=', 1)]
        safe_globals[a] = eval(b, {'__builtins__': None}, safe_globals)
        return None

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
    runs faster and scales better then a regex that has to
    calculate line numbers from my limited tests
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
        # TODO setup attributes to span multiple lines
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

def haml(f, t='hr'):
    _f = open(f).readlines()
    # process eval stuff first
    _f = parse_preprocessor(_f)
    _f = parse_py(_f)
    
    #parse document next
    l = parse_doc(_f)
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

    def render(f, t):
        def _render():
            return haml(f, t)
        return _render
    
    if t == 'r':
        test(render(f, t))
    if t == 'hr':
        test(render(f, t))
    if t == 'haml':
        print haml(f)


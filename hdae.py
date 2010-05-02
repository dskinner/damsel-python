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
import re

# this bit would create seperate groups which might be useful
# for establish what should happen, but then it might not be
# relevant with compile(... 'exec')
# re.findall(':(.*\=.*$)|:(.*\))', f, re.M)

p = re.compile(':(.*\=.*$|.*\))', re.M) # parse out : directives
p2 = re.compile('(\(.*?\))') # pull out attribute declarations

safe_locals = {'len': __builtin__.len, 'locals': __builtin__.locals}

def is_func_call(x):
    """
    determines if string is a function call.
    This differentiates between item assignment
    and a function call on the assumption that there is no space
    between func_name and the first instance of (

    # FIXME this should account for the following

        user='(Daniel)'

      by checking for = between ^ and ( index
    """
    if '(' in x and ' ' not in x[:x.index('(')]:
        return True
    return False

def func_to_locals(x):
    """
    This parses a string to be eval'd so as to add function
    calls to the locals() index, ie:

      greeting('Daniel')

    will get transformed to:

      locals()['''greeting('Daniel')'''] = greeting('Daniel')

    while calls such as:

      user = 'Daniel'

    will be left intact.
    """
    if is_func_call(x):
        return '''locals()["""{0}"""]={0}'''.format(x)
    return x

def safe_eval(s):
    return eval(s, {'__builtins__': None}, safe_locals)

def parse_eval(f):
    l = p.findall(f) # [':greeting = lambda x: x', ':greeting("meh")']
    m = [func_to_locals(x) for x in l]
    c = compile(';'.join(m), '<string>', 'exec')
    safe_eval(c) # populates safe_locals
    for x in l:
        if x in safe_locals:
            f = f.replace(':'+x, safe_locals[x])
        else:
            f = f.replace(':'+x, '')
    return f

def parse_doc(f):
    r = []
    plntxt = []
    total_a_time = 0
    
    for l in f.splitlines():
        t = l.rstrip() # remove line break endings
        if t == '':
            continue # skip blank lines

        # inspect directive, determine if plain text
        directive = t.lstrip()[0]
        if directive != '%':
            if directive == '#':
                t = t.replace('#', '%#', 1)
            elif directive == '.':
                t = t.replace('.', '%.', 1)
            else:
                plntxt.append(t)
                continue

        
        # check plntxt queue
        # 6.24656677246e-05
        # 6.72340393066e-05
        a_time = time()
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
        total_a_time += time()-a_time
        ###
        #t = t.format(**safe_locals)
        t = t.partition('%') # ('    ', '%', 'tag#id.class(attr=val) content')
        
        attr = None
        if '(' in t[2]:
            # TODO can this be done without regex? save 0.3ms
            if ' ' in t[2][:t[2].index('(')]:
                u = t[2].partition(' ') # FIXME duplicated at next else, refactor this somehow
            else:
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

        # check for : directives here
        #se = get_eval_string(u[2])
        #if se:
        #    e.text = se
        #else:
        e.text = u[2]

        
        # FIXME slow slow slow slow slow...
        # FIXME splitting attributes with ', ' but it could be so many other ways like ',' or ',  ' or ' , '
        if attr is not None:
            for x in attr[1:-1].split(', '):
                k, v = x.split('=')
                e.attrib[k] = v
        if tag[2][0] != '':
            e.attrib['id'] = tag[2][0]

        _class = tag[0][2] + ' ' + tag[2][2]
        if _class != ' ':
            e.attrib['class'] = _class.replace('.', ' ').strip()

        r.append((t[0], e))
    print 'atime', total_a_time
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
    """ FIXME something is busted here as can be seen with bench/hdae/template.html
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


def haml(f, t='r'):
    _f = open(f).read()
    # process eval stuff first
    _f = parse_eval(_f)
    
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


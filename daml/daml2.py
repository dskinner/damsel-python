#! /usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import __builtin__
except ImportError:
    import builtins as __builtin__ #Python 3.0

from lxml import etree
from time import time
from string import Formatter
import sys
import os.path
from time import time
from _fmt import DamlFormatter

class LXML(object):
    """
    Used to declare lxml.etree.tostring params by declaring attributes. This
    ends up working faster then declaring variables and scraping and is easier
    on the eyes and fingers for declaring common tostring keyword arguments
    versus the use of a traditional dict.
    """
    pass

template_dir = ''
dir_tags = {}

def safe_open(f, dir_tag=None):
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
        raise Exception('Cannot specify a relative path for opening a template.')

    if dir_tag is not None:
        if dir_tag in dir_tags:
            td = dir_tags[dir_tag]
        else:
            raise Exception('Directory tag does not exist: {0}'.format(dir_tag))
    else:
        td = template_dir

    return open(os.path.join(td, f))

def include(f, dir_tag=None):
    _f = safe_open(f, dir_tag).readlines()
    _f = _pre_parse(_f)
    _f = _py_parse(_f)
    return _f

def block(s):
    s = s.splitlines()
    s = _py_parse(s)
    safe_globals['__blocks__'][s[0]] = [s[1:], False] # [content, been-used-yet?]
    return

def safe_eval(s):
    return eval(s, safe_globals)

def to_local(i, l):
    # i should rethink this, it can lead to trouble down the road
    # TODO maybe i should generate a hash instead to index by and group it with the command
    # this could work better with fewer issues, part of the refactoring
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
    if s is not None:
        return s.replace('>', '&gt;').replace('<', '&lt;')
    return ''

def to_fmt(s):
    return "fmt.format('''{0}''')".format(s)

def _py_parse(f):
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
            queue.append((i, l, to_local(i, to_fmt(l))))
        '''
            for x in fmt.parse(l):
                if x[1] is not None:
                    queue.append((i, x[1], to_local(i, x[1])))
        '''

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
    c = compile('fmt.namespace=globals();'+cmd_s, '<string>', 'exec')
    safe_eval(c)

    ###

    offset = 0

    for e in queue:
        i = e[0]
        l = e[1]

        if l[0] != ':':
            k = '''__{0}_{1}__'''.format(i, to_fmt(l))
            #l = '{'+l+'}'
        else:
            k = '''__{0}_{1}__'''.format(i, l[1:])


        if k in safe_globals:

            v = safe_globals[k] or ''
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

def _doc_parse(f):
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
                k, v = x.split('=', 1)
                e.attrib[k.strip()] = v.strip()

        r.append((l[0], e)) # ('    ', etree.Element)
    return r

def _build(parsed):
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
                'lxml': LXML()}

# Python3
if hasattr(__builtin__, 'False'):
    safe_globals['False'] = getattr(__builtin__, 'False')

if hasattr(__builtin__, 'True'):
    safe_globals['True'] = getattr(__builtin__, 'True')
#

fmt = DamlFormatter(safe_globals)
safe_globals['fmt'] = fmt

def get_leading_whitespace(s):
    def _get():
        for x in s:
            if x != ' ':
                break
            yield x
    return ''.join(_get())

def _post_parse(s):
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


def _pre_parse2(f):
    """
    TODO normalization to the document to handle all kinds of fun whitespace
    """

    mf = None # multi-line func
    mf_ws = None # first-childs indention

    mc = None # mixed content
    offset = 0
    for i, line in enumerate(f[:]):
        l = line.strip()
        if l == '':
            f.pop(i+offset)
            offset -= 1
            continue

        ws = line.rstrip()[:-len(l)]

        # handle multiline function
        if mf is not None:
            if ws <= mf[0]:
                mf[1].append("''')")
                mf[1] = '\n'.join(mf[1])
                f[f.index(mf)] = ''.join(mf)
                mf = None
                mf_ws = None
            else:
                mf_ws = mf_ws or ws
                ws = ws[:-len(mf_ws)]
                mf[1].append(ws+l)
                f.pop(i+offset)
                offset -= 1
                continue

        # handle mixed content
        if mc is not None:
            if ws <= mc[0]:
                mc[1].append('globals()[{__i__}]=list(__mixed_content__)') # __i__ is formatted during _py_parse
                mc[1] = '\n'.join(mc[1]) # prep for py_parse
                mc = None
            else:
                if l[0] == ':':
                    l = l[1:]
                else:
                    # TODO account for mixed-indention with mixed-plaintxt
                    l = '__mixed_content__.append(fmt.format("""{0}"""))'.format(l)

                ws = ws[:-len(mc[0])]
                mc[1].append(ws+l)
                continue

        # inspect for mixed content or multiline function
        if l[0] == ':':
            if l[-1] == ':': # mixed content
                result.append([ws, [':__mixed_content__ = []', l[1:]]])
                mc = result[-1]
                continue
            elif '(' not in l and '=' not in l: # multiline function
                l = l.replace(' ', "('''", 1)
                f.pop(i+offset)
                f.insert(i+offset, [ws, [l]])
                mf = f[i+offset]
                continue
    for x in f:
        print `x`
    return f


def _pre_parse(f):
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
    offset = 0

    mf = None # [parent-indent, first-child-indent, parent-index, string-list]
    mc = None

    for i, line in enumerate(f[:]):
        l = line.rstrip()
        if l == '':
            f.pop(i+offset)
            offset -= 1
            continue
        
        d = l.strip()
        ws = l[-len(d)]
        
        # check queue if we need to append this line
        if mf is not None:
            #check indention and append appropriately
            #ws = get_leading_whitespace(l) # should keep up with this data and never call this func again
            if ws > mf[0]:
                f.pop(i+offset)
                offset -= 1
                if mf[1] is None:
                    mf[1] = ws
                mf[3].append(l[len(mf[1]):])
            else: # handle and clear queue once indention decreases to right place
                mf[3].append("')\n")
                f.insert(mf[2]+1, '\\n'.join(mf[3])) #insert after, not before
                offset += 1
                mf = None

        #
        
        directive = d[0] # if i keep the preprocessor, stuff like this might be able to get saved for use by parser

        while mc is not None:
            mc_ws, mc_i, mc_confirm, fc_space = mc

            #ws = get_leading_whitespace(l)

            if directive == ':':
                if d[1] == ' ':
                    mc[3] = None
                    break
                else:
                    if mc_confirm:
                        f.insert(mc_i, mc_ws+':__mixed_content__ = []') # find note below on mc_i
                        offset += 1
                        f.insert(i+offset, mc_ws+':list(__mixed_content__)')
                        offset += 1

                    mixed_content = None
                    break
                    # breaks out of if statement, make this a loop?
            else:
                if ws <= mc_ws:
                    if mc_confirm:
                        f.insert(mc_i, mc_ws+':__mixed_content__ = []')
                        offset += 1
                        f.insert(i+offset, mc_ws+':list(__mixed_content__)')
                        offset += 1

                    mc = None
                    break
                    # break out of if statement, make this a loop?
                else:
                    # convert to fmt.format()
                    mc[2] = True
                    if fc_space is None:
                        mc[3] = fc_space = ' '*((len(ws)-len(mc_ws))-1)
                        cmd_space = ''
                    else:
                        cmd_space = ' '*(len(ws)-len(fc_space)-len(mc_ws))
                    cmd_template = '{0}:{1}__mixed_content__.append(fmt.format("""{2}{3}"""))'

                    new_cmd = cmd_template.format(mc_ws, fc_space, cmd_space, d) #-1 to follow standard tabspaces
                    f.pop(i+offset)
                    f.insert(i+offset, new_cmd)
                    break


        if directive == ':':
            if d[-1] == ':':
                if mc is None:
                    #ws = l.partition(':')[0]
                    """
                    since blank lines are getting dropped, we want to store the original offset value of
                    the start of the mixed_content, and when calling it back, we do not want to +offset
                    it as the offset count isn't relevant anymore
                    """
                    mc = [ws, i+offset, False, None] # [orig-whitespace, orig-index, confirm-mixed-content, first-plaintext-indent] this just means a Possibility of mixed_content
                    continue

            elif '(' not in d and '=' not in d: # last rule is for if's and for's
                f.pop(i+offset)
                offset -= 1

                y = d.partition(' ')
                #ws = l.partition(':')[0]

                mf = [ \
                    ws,    # original whitespace
                    None,                   # first childs whitespace
                    i+offset,               # original index
                    [ws+y[0]+"('"+y[2]]]             # build string

                continue

            elif d[:9] == ':extends(': #factor this out, should only run at top of document, not every effin line
                nf = safe_open(l.split("'")[1]).readlines() # FIXME safe_open
                nf = parse_preprocessor(nf) # for multi-depth :extends(...)
                f.pop(i+offset)
                offset -= 1
                for y in nf:
                    offset += 1
                    f.insert(i+offset, y)

    if mf is not None: # ugh, one last check, need better solution for this
        mf[3].append("')\n")
        f.append('\\n'.join(mf[3]))

    if mc is not None:
        if mc_confirm:
            f.insert(mc_i, mc_ws+':__mixed_content__ = []')
            offset += 1
            f.insert(i+offset+1, mc_ws+':list(__mixed_content__)') #offset +1 ? this is buggy, something to do with being end of document?
            offset += 1

        mc = None

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
    safe_globals.update(sandbox)
    # process eval stuff first
    #f = _pre_parse(f)
    f = _pre_parse2(f)
    #print f
    f = _py_parse(f)
    l = _doc_parse(f)
    b = _build(l)

    s = tostring(b[0][1])
    safe_globals = copy(_safe_globals)
    s = _post_parse(s)
    return s


if __name__ == '__main__':
    import sys
    from time import time
    f = sys.argv[1]
    t = sys.argv[2]

    f = safe_open(f).readlines()

    if t == 'y':
        times = []
        for x in range(2000):
            a = time()
            _safe_globals = copy(safe_globals)
            #safe_globals['lxml'] = LXML()
            #parse_py(parse_preprocessor(f))
            parse(f)
            times.append(time()-a)
            safe_globals = copy(_safe_globals)
        print min(times)
    else:
        print parse(f)
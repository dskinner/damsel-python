# -*- coding: utf-8 -*-
"""
eval('len("asdf")', {"__builtins__":None}, {'len': __builtin__.len})
"""
import __builtin__
import re

from daml import parse_preprocessor

p = re.compile(':(.*\=.*$|.*\))', re.M)
p2 = re.compile(':(.*\=.*$)|(:.*\))', re.M)

p3 = re.compile(':[\w\d\s]*$')

safe_locals = {'len': __builtin__.len, 'locals': __builtin__.locals}

def test_multiline_join(f):
    for x in range(24):
        b=parse_preprocessor(f)

def test_cond_builtin():
    a = '''            :some just stuff junk yeah'''
    for x in range(1000):
        b = a.lstrip()
        if b[0] == ':' and '=' not in b and '(' not in b:
            a

def test_cond_regex():
    a = '''            :some just stuff junk yeah'''
    for x in range(1000):
        p3.search(a)

def get_whitespace_partition():
    a = '''            :some just stuff junk yeah'''
    for x in range(10000):
        indention = a.partition(':')[0]

def get_whitespace_split():
    a = '''            :some just stuff junk yeah'''
    for x in range(10000):
        indention = a.split(':')[0]

def safe_eval(s):
    return eval(s, {'__builtins__': None}, safe_locals)

def to_local(i, l):
    return '''locals()["""__{0}_{1}__"""]={1}'''.format(i, l)

def parse_call(i, l):
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

from string import Formatter
fmt = Formatter()

def parse_py():
    """
    runs faster and scales better then a regex that has to
    calculate line numbers
    """
    f = open('bench/hdae/template.html').readlines()
    queue = []
    sss_total = 0
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
        sss = time()
        if '{' in l:
            for x in fmt.parse(l):
                if x[1] is not None:
                    queue.append((i, x[1], to_local(i, x[1])))
        sss_total += time()-sss

        # look to see if :directive is embedded in line
        if ':' in l:
            a = l.index(':')
        if '(' in l:
            b = l.index('(')
        else:
            continue
        if ' ' in l[a:b]:
            continue
        c = l.index(')')+1
        queue.append((i, l[a:c], to_local(i, l[a+1:c])))

    print '@@@@@@@@@', sss_total

    c = compile(';'.join([x[2] for x in queue]), '<string>', 'exec')
    safe_eval(c)

    for e in queue:
        i = e[0]
        l = e[1]
        
        if l[0] != ':':
            k = '''__{0}_{1}__'''.format(i, l)
            l = '{'+l+'}'
        else:
            k = '''__{0}_{1}__'''.format(i, l[1:])
        
        if k in safe_locals:
            f[i] = f[i].replace(l, safe_locals[k], 1)
        else:
            f[i] = f[i].replace(l, '', 1)
        
    return f




def func_to_locals(x):
    """
    This parses a string to be eval'd so as to add function
    calls to the locals() index, ie:

      greeting('Daniel')
    
    will get transformed to:

      locals()['''greeting('Daniel')'''] = greeting('Daniel')

    while calls such as:

      user = 'Daniel'

    will be left intact. This differentiates between item assignment
    and a function call on the assumption that there is no space
    between func_name and the first instance of (
    
    # FIXME this should account for the following

        user='(Daniel)'

      by checking for = between ^ and ( index
    """
    if '(' in x and ' ' not in x[:x.index('(')]:
        return '''locals()["""{0}"""]={0}'''.format(x)
    return x





def re_sub_test():
    f = open('bench/hdae/template.html').read()
    #l = p.findall(f)
    l = [(f.count('\n', 0, m.start()), m.group(1)) for m in p.finditer(f)]
    return l
    
    
def str_replace_test():
    f = open('bench/hdae/template.html').read()
    l = p.findall(f)
    for x in l:
        f = f.replace(x, '!!!!!!!!!!!')

l_replace = lambda f, x: f.replace(x, '!!!!!!!!!!!')
def test_lambda():
    f = open('bench/hdae/template.html').read()
    l = p.findall(f)
    for x in l:
        l_replace(f, x)

def compile_and_eval(f):
    l = p.findall(f)
    l = [func_to_locals(x) for x in l]
    c = compile(';'.join(l), '<string>', 'exec')
    safe_eval(c)


def test_p():
    for x in range(1):
        f = open('bench/hdae/template.html').read()
        compile_and_eval(f)

def test_p2():
    for x in range(2):
        f = open('bench/hdae/template.html').read()
        l = p2.findall(f)

def test_eval():
    loc = {}
    new_l = []
    for x in l:
        if x[0] == ':':
            x = x.replace(':', '''locals()["""{0}"""]='''.format(x[1:]), 1)
        new_l.append(x)
    c = compile(';'.join(new_l), '<string>', 'exec')
    eval(c, {}, loc)


if __name__ == '__main__':
    from time import time
    times = []
    f = open('test/templates/pre_multiline_method.daml').readlines()
    for x in range(10):
        a = time()
        test_multiline_join(f)
        times.append(time()-a)
    print min(times)


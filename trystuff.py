# -*- coding: utf-8 -*-
"""
eval('len("asdf")', {"__builtins__":None}, {'len': __builtin__.len})
"""
import __builtin__
import re

p = re.compile(':(.*\=.*$|.*\))', re.M)
p2 = re.compile(':(.*\=.*$)|(:.*\))', re.M)

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



safe_locals = {'len': __builtin__.len, 'locals': __builtin__.locals}


def re_sub_test():
    f = open('bench/hdae/template.html').read()
    l = p.findall(f)
    for x in l:
        f = re.sub(re.escape(x), '!!!!!!!!!!!', f)
    
    
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

def safe_eval(s):
    return eval(s, {'__builtins__': None}, safe_locals)


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

from time import time

times = []
for x in range(10):
    a = time()
    test_lambda()
    times.append(time()-a)
print min(times)
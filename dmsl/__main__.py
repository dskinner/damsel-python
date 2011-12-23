import argparse
import ast
import timeit
import os

from _parse import Template
import _sandbox

def parse(template, context, _locals, timed, cache, repeat):
    # use of extensions to inject _locals
    _sandbox.extensions = _locals
    try:
        if timed and cache:
            t = timeit.Timer('tpl.render()', 'from __main__ import Template\ntpl = Template("{0}")\ncontext={1}'.format(template, str(context)))
            print '%.2f ms %s' % (1000 * t.timeit(100)/100, template)
        elif timed:
            t = timeit.Timer('Template("{0}").render()'.format(template), 'from __main__ import Template')
            print '%.2f ms %s' % (1000 * t.timeit(repeat)/repeat, template)
        else:
            t = Template(template)
            print(t.render(**context))
            #print '<!DOCTYPE html>\n'+etree.tostring(etree.fromstring(t.render(**context)), pretty_print=True)
    except Exception as e:
        print 'Exception rendering ', template
        print e

def parse_templates(templates, context, _locals, timed, cache, repeat):
    for template in templates:
        path = os.path.join(_sandbox._open.template_dir, template)

        if os.path.isfile(path):
            parse(template, context, _locals, timed, cache, repeat)
        elif os.path.isdir(path):
            files = get_files(path)
            for e in files:
                # make paths relative to template directory again
                e = e.replace(_sandbox._open.template_dir, '', 1)
                parse(e, context, _locals, timed, cache, repeat)

def get_files(directory):
    files = []
    for e in os.listdir(directory):
        path = os.path.join(directory, e)
        if os.path.isfile(path) and os.path.splitext(path)[1] == '.dmsl':
            files.append(path)
        elif os.path.isdir(path):
            files.extend(get_files(path))
    return files

parser = argparse.ArgumentParser(description='Render dmsl templates.')
parser.add_argument('templates', metavar='F', type=str, nargs='+', help='Location of dmsl template file(s). If given a directory, will traverse and locate dmsl templates.')
parser.add_argument('--kwargs', dest='kwargs', type=ast.literal_eval, nargs=1, default=[{}], help='Specify a dict as a string, i.e. "{\'a\': \'b\'}", thats parsed with ast.literal_eval for use as a \
    template\'s kwargs during parse. This is the same as calling Template(\'test.dmsl\').render(**kwargs)')
parser.add_argument('--locals', dest='_locals', type=ast.literal_eval, nargs=1, default=[{}], help='Specify a dict that will be used to inject locals for use by template (Useful for testing template blocks). \
    See --kwargs for example. If timing parse, keep in mind that these variables already exist in memory and are not instantiated in the template.')
parser.add_argument('--template-dir', dest='template_dir', type=str, nargs=1, default=None, help='If a template directory is given, templates should be specified local to that directory. Useful for testing templates \
    with include and extends.')
parser.add_argument('--timeit', dest='timed', action='store_const', const=True, default=False, help='Time the duration of parse.')
parser.add_argument('--cache', dest='cache', action='store_const', const=True, default=False, help='When timing parse,  prerender portions of the template and time final render.')
parser.add_argument('--repeat', dest='repeat', type=int, nargs=1, default=[100], help='When timing parse, specify number of runs to make.')
parser.add_argument('--debug', dest='debug', action='store_const', const=True, default=False, help='Parser step output for debugging module and templates. Negates any other options set (except --template-dir) and only applicable for parsing a single template file.')

args = parser.parse_args()

if args.template_dir is not None:
    _sandbox._open.template_dir = args.template_dir[0]

if not args.debug:
    parse_templates(args.templates, args.kwargs[0], args._locals[0], args.timed, args.cache, args.repeat[0])
else:
    import pprint
    from _pre import _pre
    from _py import _compile

    pp = pprint.PrettyPrinter(depth=3)

    fn = args.templates[0]
    f = _sandbox._open(fn).read().splitlines()
    r, py_q = _pre(f)
    print('\n!!! r !!!\n')
    pp.pprint(r)
    print('\n@@@ py_q @@@\n')
    pp.pprint(py_q)
    print('\n### py_str ###\n')
    code, py_str = _compile(py_q, fn)
    print(py_str)
    print('\n$$$$$$$$$$\n')





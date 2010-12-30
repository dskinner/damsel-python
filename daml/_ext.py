# Default set of dmsl extensions

def block(s):
    s = s.splitlines()
    n = s[0]
    s = s[1:]
    block.blocks[n] = s
block.blocks = {}

def css(s):
    s = s.splitlines()
    n = s[0]
    s = s[1:]
    return [u'%link[rel=stylesheet][href={0}{1}]'.format(n, x) for x in s]

def js(s):
    s = s.splitlines()
    n = s[0]
    s = s[1:]
    return ['%script[src={0}{1}]'.format(n, x) for x in s]

extensions = {'block': block,
              'css': css,
              'js': js}
def parse_attr(s):
    j = 0
    for i, c in enumerate(s):
        if c == ' ' and j == 0:
            return s[:i]+s[i:], ''
        elif c == '(':
            j = i
        elif c == ')':
            i += 1
            return s[:j]+s[i:], s[j:i]
    return s, ''

def parse2(s):
    j = 0
    attrs = []
    tags = ''
    for i, c in enumerate(s):
        if c == '[':
            j = i
        elif c == ']':
            attrs.append(s[j:i+1])
            tags += s[:j]+s[i+1:]
    return tags, attrs


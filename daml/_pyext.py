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


def parse_attr2(s):
    mark_start = None
    mark_end = None

    key_start = None
    val_start = None
    literal_start = None

    d = {}

    for i, c in enumerate(s):
        if key_start is not None:
            if val_start is not None:
                if i == val_start+1 and (c == '"' or c == "'"):
                    literal_start = i
                elif literal_start is not None and c == s[literal_start]:
                    d[s[key_start+1:val_start]] = s[literal_start+1:i]
                    key_start = None
                    val_start = None
                    literal_start = None
                elif literal_start is None and c == ']':
                    d[s[key_start+1:val_start]] = s[val_start+1:i]
                    key_start = None
                    val_start = None
            elif c == '=':
                val_start = i
        elif c == '[':
            key_start = i
            if mark_start is None:
                mark_start = i
        elif c == ' ':
            mark_end = i
            break
    
    if mark_start is None:
        return s, d
    if mark_end is None:
        return s[:mark_start], d
    else:
        return s[:mark_start]+s[mark_end:], d
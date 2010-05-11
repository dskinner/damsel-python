# -*- coding: utf-8 -*-

class Element(object):
    def __init__(self, s):
        self.parent = None
        self.children = []
        self.attr = {}
        self.text = []
        self.tail = []
        self.parse(s)

    def append(self, child):
        child.parent = self
        self.children.append(child)
    
    def to_string(self):
        a = '<'+self.name
        for k, v in self.attr.items():
            a += ' '+k+'="'+v+'"'
        a +='>'+''.join(self.text)
        for x in self.children:
            a += x.to_string()
        a += '</'+self.name+'>'+' '.join(self.tail)
        return a

    def parse(self, s):
        if s[0] == '%':
            s = s[1:]

        i = s.find('(')
        if i != -1:
            j = s.index(')')+1
            attr = s[i:j]
            s = s.replace(attr, '')
            for x in attr[1:-1].split(','):
                k, tmp, v = x.partition('=')
                self.attr[k.strip()] = v.strip()
        
        s = s.partition(' ')
        self.text.append(s[2])
        
        tag = [x.partition('.') for x in s[0].partition('#')]

        self.name = tag[0][0] or 'div'
        if tag[2][0] != '':
            self.attr['id'] = tag[2][0]
        cls = tag[0][2] + ' ' + tag[2][2]
        if cls != ' ':
            self.attr['class'] = cls.replace('.', ' ')

        
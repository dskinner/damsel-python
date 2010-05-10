# -*- coding: utf-8 -*-

class Element(object):
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.children = []
        self.attrib = {}
        self.text = ''
        self.tail = ''

    def append(self, child):
        child.parent = self
        self.children.append(child)
    
    def to_string(self):
        a = '<'+self.name
        for k, v in self.attrib.items():
            a += ' '+k+'="'+v+'"'
        a +='>'+self.text
        for x in self.children:
            a += x.to_string()
        a += '</'+self.name+'>'+self.tail
        return a
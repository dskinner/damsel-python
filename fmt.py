# -*- coding: utf-8 -*-
from string import Formatter

class NamespaceFormatter(Formatter):
    def __init__(self, namespace={}):
        Formatter.__init__(self)
        self.namespace = namespace

    def get_value(self, key, args, kwds):
        return self.namespace[key]
# -*- coding: utf-8 -*-
from string import Formatter

class FormatSpecs(object):
    def safe(self, value):
        return value
    def title(self, value):
        return value.title()
    def escape(self, value):
        return value.replace('<', '&lt;').replace('>', '&gt;')


cdef inline str _fmt(str s, tuple args, dict kwargs):
    s = s.format(*args, **kwargs)
    if '<' in s:
        s.replace('<', '&lt;')
    if '>' in s:
        s.replace('>', '&gt;')
    return s

def fmt(__fmt_string__, *args, **kwargs):
    return _fmt(__fmt_string__, args, kwargs)

"""
class DMSLFormatter(Formatter):
    def __init__(self, namespace={}):
        Formatter.__init__(self)
        self.namespace = namespace
        self.format_specs = FormatSpecs()
    
    def format(self, __fmt_string__, *args, **kwargs):
        return fmt(__fmt_string__, self.namespace, args, kwargs)

    def format_field(self, value, format_spec):
        # default to escape
        #if isinstance(value, (int, float)):
        #    return format(value, format_spec)

        #format_spec = format_spec or 'escape'

        #if hasattr(self.format_specs, format_spec):
        #    return getattr(self.format_specs, format_spec)(value)
        return format(value, format_spec)

    def get_value(self, key, args, kwargs):
        '''
        args are reserved for inline python/dmsl functions while kwargs
        is reserved for globals(), which is passed in as the namespace upon
        instantiation of class
        '''
        if isinstance(key, (int, long)):
            return args[key]
        elif key in kwargs:
            return kwargs[key]
        else:
            return self.namespace[key]
"""

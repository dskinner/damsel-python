# -*- coding: utf-8 -*-
import os.path
import unittest
#from _parse import c_parse as parse
from _parse import Template
import codecs

class TestBasic(unittest.TestCase):
    def setUp(self):
        self.t = {
            'basic_html': None,
            'basic_indent': None,
            'basic_inline': None,
            'basic_multilinetext': None,
            'basic_tag_hashes': None,
            'basic_variable_indent': None
            }

        for k, v in self.t.items():
            # template file
            a = k+'.dmsl'
            # expected output
            b = open(os.path.join('', k+'.html')).read()
            self.t[k] = (a, b)

    def test_basic_html(self):
        parsed, expected = self.t['basic_html']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())
    
    def test_basic_indent(self):
        parsed, expected = self.t['basic_indent']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())
        
    def test_basic_inline(self):
        parsed, expected = self.t['basic_inline']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())
    
    def test_basic_multilinetext(self):
        parsed, expected = self.t['basic_multilinetext']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())
    
    def test_basic_tag_hashes(self):
        parsed, expected = self.t['basic_tag_hashes']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())
    
    def test_basic_variable_indent(self):
        parsed, expected = self.t['basic_variable_indent']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())


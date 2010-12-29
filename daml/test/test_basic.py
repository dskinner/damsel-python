# -*- coding: utf-8 -*-
import os.path
import unittest
from _parse import parse_new as parse
import codecs

class TestBasic(unittest.TestCase):
    def setUp(self):
        self.t = {
            'basic_html': None,
            'basic_indent': None,
            'basic_inline': None,
            'basic_tag_hashes': None,
            'basic_variable_indent': None
            }

        for k, v in self.t.items():
            # template file
            a = k+'.daml'
            # expected output
            b = open(os.path.join('', k+'.html')).read()
            self.t[k] = (a, b)

    def test_basic_html(self):
        parsed, expected = self.t['basic_html']
        parsed = parse(parsed)
        self.assertEqual(parsed.strip(), expected.strip())
    
    def test_basic_indent(self):
        parsed, expected = self.t['basic_indent']
        parsed = parse(parsed)
        self.assertEqual(parsed.strip(), expected.strip())
        
    def test_basic_inline(self):
        parsed, expected = self.t['basic_inline']
        parsed = parse(parsed)
        self.assertEqual(parsed.strip(), expected.strip())
    
    def test_basic_tag_hashes(self):
        parsed, expected = self.t['basic_tag_hashes']
        parsed = parse(parsed)
        self.assertEqual(parsed.strip(), expected.strip())
    
    def test_basic_variable_indent(self):
        parsed, expected = self.t['basic_variable_indent']
        parsed = parse(parsed)
        self.assertEqual(parsed.strip(), expected.strip())


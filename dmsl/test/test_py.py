# -*- coding: utf-8 -*-
import os.path
import unittest
from _parse import c_parse as parse
#from _parse import parse
import codecs

class TestPy(unittest.TestCase):
    def setUp(self):
        self.t = {
            'py_block_default': None,
            'py_embed': None,
            'py_extends': None,
            'py_formatter': None,
            'py_func': None,
            'py_ifelse': None,
            'py_include': None,
            'py_looping': None,
            'py_mixed_content': None,
            'py_nested_for': None,
            'py_newline_var': None
            }

        for k, v in self.t.items():
            # template file
            a = k+'.dmsl'
            # expected output
            b = open(os.path.join('', k+'.html')).read()
            self.t[k] = (a, b)

    def test_py_block_default(self):
        parsed, expected = self.t['py_block_default']
        parsed = parse(parsed)
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_embed(self):
        parsed, expected = self.t['py_embed']
        parsed = parse(parsed)
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_extends(self):
        parsed, expected = self.t['py_extends']
        parsed = parse(parsed)
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_formatter(self):
        parsed, expected = self.t['py_formatter']
        parsed = parse(parsed)
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_func(self):
        parsed, expected = self.t['py_func']
        parsed = parse(parsed)
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_ifelse(self):
        parsed, expected = self.t['py_ifelse']
        parsed = parse(parsed)
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_include(self):
        parsed, expected = self.t['py_include']
        parsed = parse(parsed)
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_looping(self):
        parsed, expected = self.t['py_looping']
        parsed = parse(parsed)
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_mixed_content(self):
        parsed, expected = self.t['py_mixed_content']
        parsed = parse(parsed)
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_nested_for(self):
        parsed, expected = self.t['py_nested_for']
        parsed = parse(parsed)
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_newline_var(self):
        parsed, expected = self.t['py_newline_var']
        parsed = parse(parsed)
        self.assertEqual(parsed.strip(), expected.strip())


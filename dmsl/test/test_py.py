# -*- coding: utf-8 -*-
import os.path
import unittest
#from _parse import c_parse as parse
from _parse import Template
import codecs

class TestPy(unittest.TestCase):
    def setUp(self):
        self.t = {
            'py_block_default': None,
            'py_complex1': None,
            'py_complex2': None,
            'py_complex3': None,
            'py_embed': None,
            'py_ending_colon': None,
            'py_extends': None,
            'py_formatter': None,
            'py_func': None,
            'py_ifelse': None,
            'py_ifordering': None,
            'py_if_nested': None,
            'py_include': None,
            'py_looping': None,
            'py_mixed_content': None,
            'py_nested_for': None,
            'py_newline_var': None,
            'py_raise': None
            }

        for k, v in self.t.items():
            # template file
            a = k+'.dmsl'
            # expected output
            b = open(os.path.join('', k+'.html')).read()
            self.t[k] = (a, b)

    def test_py_block_default(self):
        parsed, expected = self.t['py_block_default']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())
    
    def test_py_complex1(self):
        parsed, expected = self.t['py_complex1']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())
    
    def test_py_complex2(self):
        parsed, expected = self.t['py_complex2']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())
    
    def test_py_complex3(self):
        parsed, expected = self.t['py_complex3']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_embed(self):
        parsed, expected = self.t['py_embed']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_ending_colon(self):
        parsed, expected = self.t['py_ending_colon']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_extends(self):
        parsed, expected = self.t['py_extends']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_formatter(self):
        parsed, expected = self.t['py_formatter']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_func(self):
        parsed, expected = self.t['py_func']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_ifelse(self):
        parsed, expected = self.t['py_ifelse']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())
    
    def test_py_ifordering(self):
        parsed, expected = self.t['py_ifordering']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())
    
    def test_py_if_nested(self):
        parsed, expected = self.t['py_if_nested']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_include(self):
        parsed, expected = self.t['py_include']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_looping(self):
        parsed, expected = self.t['py_looping']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_mixed_content(self):
        parsed, expected = self.t['py_mixed_content']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_nested_for(self):
        parsed, expected = self.t['py_nested_for']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_newline_var(self):
        parsed, expected = self.t['py_newline_var']
        parsed = Template(parsed).render()
        self.assertEqual(parsed.strip(), expected.strip())
    
    def test_py_raise(self):
        parsed, expected = self.t['py_raise']
        #TODO fix this test for 2.6
        self.assertRaises(Exception, Template(parsed).render)
        #self.assertEquals(str(e.exception), 'Testing raise Exception("...")')



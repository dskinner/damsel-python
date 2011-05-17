# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.getcwd())

import unittest
from test_basic import *
from test_py import *
import dmsl

#os.chdir('test/templates')
dmsl.template_dir = 'test/templates'
unittest.main()

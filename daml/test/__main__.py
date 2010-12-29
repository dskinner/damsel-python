# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.getcwd())

import unittest
from _parse import parse_new
from test_basic import *
from test_py import *

#daml.template_dir = 'test/templates'
os.chdir('test/templates')
unittest.main()
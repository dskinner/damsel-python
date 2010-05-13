# -*- coding: utf-8 -*-
"""
import daml
daml._sandbox._open.template_dir = 'omg/seriously'
daml.parse('index.daml', {'content': 'Hello World!'})
"""
__version__ = '0.1.2.99'
from _parse import parse

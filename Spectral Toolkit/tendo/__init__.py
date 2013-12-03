#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license for licensing details.
from __future__ import absolute_import

__author__ = "Sorin Sbarnea"
__copyright__ = "Copyright 2010-2013, Sorin Sbarnea"
__email__ = "sorin(dot)sbarnea(at)gmail.com"
__status__ = "Production"
__date__ = "2013-09-10"

__all__ = ['singleton']

"""
Tendo is tested with Python 2.5-3.3
"""

import sys
if sys.hexversion < 0x02050000:
    sys.exit("Python 2.5 or newer is required by tendo module.")

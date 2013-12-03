#!/usr/bin/env python
# -*- coding: utf-8 -*- 

'''
Created on Sep 16, 2013

@author: Wiehan
'''

from tendo import singleton
me = singleton.SingleInstance()

import os, ctypes
if os.name == 'posix':
    try:
        x11 = ctypes.cdll.LoadLibrary('libX11.so')
        x11.XInitThreads()
    except:
        print "Warning: failed to XInitThreads()"

import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] ='PySide'

from PySide.QtGui import *
from PySide.QtCore import *
import sys, multiprocessing
import fftw_wrapper.fftw_py as mfftw

qt_app = QApplication(sys.argv)

from gui.library.libraryview import Library

mfftw.import_wisdom()
     
app = Library()
app.run()
qt_app.exec_()

mfftw.export_wisdom()
sys.exit()

#!/usr/bin/env python
# -*- coding: utf-8 -*- 

'''
Created on Sep 16, 2013

@author: Wiehan
'''

import os, ctypes, sys, multiprocessing, matplotlib

CPU_COUNT = multiprocessing.cpu_count()
if sys.platform == "darwin":
    print "Multi-processing is buggy on Macs. Reverting to single-threaded computation."
    CPU_COUNT = 1
    
print "Using", CPU_COUNT, "cpu cores"



if __name__ == "__main__":
    
    from tendo import singleton
    me = singleton.SingleInstance()
    
    from PySide.QtGui import *
    from PySide.QtCore import *
    import sys, multiprocessing
    import fftw_wrapper.fftw_py as mfftw
    
    if os.name == 'posix' and sys.platform != "darwin":
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"
    
    matplotlib.use('Qt4Agg')
    matplotlib.rcParams['backend.qt4'] ='PySide'
    qt_app = QApplication(sys.argv)
    
    
    
    from gui.library.libraryview import Library
    
    mfftw.import_wisdom()
         
    app = Library()
    app.run()
    qt_app.exec_()
    
    mfftw.export_wisdom()
    sys.exit()

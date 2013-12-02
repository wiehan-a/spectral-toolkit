'''
Created on Sep 16, 2013

@author: Wiehan
'''

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

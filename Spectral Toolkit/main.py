'''
Created on Sep 16, 2013

@author: Wiehan
'''

import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] ='PySide'

from PySide.QtGui import *
from PySide.QtCore import *
from gui.library.libraryview import Library
import sys, multiprocessing
import fftw_wrapper.fftw_py as mfftw

mfftw.import_wisdom()
 
qt_app = QApplication(sys.argv)
                                
app = Library()
app.run()
qt_app.exec_()

# import verslag.ar_spectrum_stats_c
 
mfftw.export_wisdom()
sys.exit()

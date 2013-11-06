'''
Created on Sep 16, 2013

@author: Wiehan
'''

import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'

from PySide.QtGui import *
from PySide.QtCore import *
import sys, os, time
from gui.downloader.downloader import Downloader
from gui.library.libraryview import Library
import fftw_wrapper.fftw_py as mfftw
import numpy as np
from data_processing.filter_design import *
from data_processing.convolution import *
from data_processing.windowing import *
from data_processing.multirate import *
from data_processing.spectral_estimation import *
from data_processing.sigproc import *
mfftw.import_wisdom()
 
qt_app = QApplication(sys.argv)
                                
app = Library()
app.run()
qt_app.exec_()

# import verslag.ar_spectrum_stats_c
 
mfftw.export_wisdom()
sys.exit()

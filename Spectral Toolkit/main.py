'''
Created on Sep 16, 2013

@author: Wiehan
'''

from PySide.QtGui import *
from PySide.QtCore import *
import sys, os
from gui.downloader.downloader import Downloader
from gui.library.libraryview import Library
import fftw_wrapper.fftw_py as mfftw

mfftw.import_wisdom()
 
import benchmarks.convolution

# qt_app = QApplication(sys.argv)
#  
# app = Library()
# app.run()
# qt_app.exec_()

#from data_processing.convolution import *
# from data_processing.filter_design import *
# import numpy as np
# import data_access.segy as segy
# 
# filt = design_low_pass_fir(1, 1, 60, 125)
# print len(filt)
# 
# import matplotlib.pyplot as plt
# 
# print dir(mfftw)
# 
# plt.plot(filt, 'x')
# 
# N = 10000
# FILT = mfftw.real_fft(filt, N)
# 
# plt.plot(filt, '-')
# plt.show()
# 
# plt.plot(125*np.arange(N/2+1)/5000.0, 10*np.log10(np.abs(FILT)))
# plt.show()
 
mfftw.export_wisdom()
sys.exit()
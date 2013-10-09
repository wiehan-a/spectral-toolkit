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

 
#import benchmarks.autocorrelation

# from data_access.segy import *

# import benchmarks.ar

# import benchmarks.discontinuity

# data = read_in_segy(['2011.08.04-00.00.00.FR.MGN.00.CGE.SEGY', '2011.08.05-00.00.00.FR.MGN.00.CGE.SEGY', '2011.08.06-00.00.00.FR.MGN.00.CGE.SEGY'])
# 
# 
# x = time.clock()
# print auto_correlation(data, maximum_lag=20)
# print time.clock() - x

# plt.plot(data)
# plt.show()

# filter = design_low_pass_fir(10, 0.1, 120, 500)
# print len(filter)
# print filter
# 
# N = 10*len(filter)
# FILT = mfftw.real_fft(filter, N)
# plt.plot(500.0*np.arange(N/2+1)/N/2, 10*np.log10(np.abs(FILT)))
# plt.show()
# N = 2**(int(np.log2(500000)))
# FILT = mfftw.real_fft(filter, N)
# print len(FILT)
  
# plt.plot(filter, '-')
# plt.show()
#  
# plt.plot(500.0*np.arange(N/2+1)/N, 20*np.log10(np.abs(FILT)))
# plt.show()

# x = time.clock()
# data = fast_convolve_fftw_w(data, filter)
# print time.clock() - x

# plt.plot(data)
# plt.show()

# print len(data)
# x = time.clock()
# data = decimate(data, 10, 500)
# data = decimate(data, 10, 500 / 10)
# data = decimate(data, 10, 500 / 100)
# data = decimate(data, 10, 0.5)
# print time.clock() - x
# print len(data)
# 
# plt.plot(data)
# plt.show()

# x = time.clock()
# apply_blackman(data)
# print time.clock() - x
 
# x = time.clock()
# transform = periodogram(data, interpolation_factor=15)
# print time.clock() - x
# plt.plot((0.025 / len(transform)) * np.arange(len(transform)), 10 * np.log10(transform))

# x = time.clock()
# transform = welch(data, len(data)/4, interpolation_factor=5)
# print time.clock() - x
# plt.plot((0.025 / len(transform)) * np.arange(len(transform)), 10 * np.log10(transform))
# plt.show()

#import data_processing.peak_detection

qt_app = QApplication(sys.argv)
             
app = Library()
app.run()
qt_app.exec_()

# from data_processing.convolution import *
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

'''
Created on Sep 16, 2013

@author: Wiehan
'''

from PySide.QtGui import *
from PySide.QtCore import *
import sys, os, time
from gui.downloader.downloader import Downloader
from gui.library.libraryview import Library
import fftw_wrapper.fftw_py as mfftw
import matplotlib.pyplot as plt
import numpy as np
from data_processing.filter_design import *
from data_processing.convolution import *
from data_processing.windowing import *

mfftw.import_wisdom()
 
#import benchmarks.convolution

from data_access.segy import *

# import benchmarks.convolution

data = read_in_segy(['2011.08.04-00.00.00.FR.MGN.00.CGE.SEGY'])

# plt.plot(data)
# plt.show()

filter = design_low_pass_fir(1, 0.1, 120, 500)
print len(filter)
print filter

N = 10*len(filter)
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

x = time.clock()
data = fast_convolve_fftw_w(data, filter)
print time.clock() - x

# plt.plot(data)
# plt.show()
x = time.clock()
apply_blackman(data)
print time.clock() - x

x = time.clock()
transform = mfftw.real_fft(data, len(data))
print time.clock() - x
plt.plot((250.0/len(transform))*np.arange(len(transform)), 20*np.log10(np.abs(transform)))
plt.show()

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
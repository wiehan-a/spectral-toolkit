'''
Created on Sep 30, 2013

@author: Wiehan
'''

import numpy as np
from data_processing.sigproc import *
import time

from data_access.segy import *
import fftw_wrapper.fftw_py as mfftw
import matplotlib.pyplot as plt

arrx = read_in_segy(['2011.08.04-00.00.00.FR.MGN.00.CGE.SEGY'])

#arrx = np.arange(0, 10000000, 0.5, dtype=np.float64)

start_time = time.clock()
x = auto_correlation(arrx, maximum_lag=3)
print x
print 'slow correl',  time.clock() - start_time

start_time = time.clock()
y = auto_correlation_fft(arrx, maximum_lag=3)
print y
print 'fast correl', time.clock() - start_time

print 'error', np.sum(np.square(x - y)/len(arrx))
'''
Created on Sep 30, 2013

@author: Wiehan
'''

import numpy as np
from data_processing.sigproc import *
from data_processing.convolution import *
import time
from data_access.segy import *
import fftw_wrapper.fftw_py as mfftw
import matplotlib.pyplot as plt
from data_processing.display_friendly import *

import pstats, cProfile

arrx = read_in_segy(['2011.08.04-00.00.00.FR.MGN.00.CGE.SEGY'])

FILT = 20*np.log10(np.abs(mfftw.real_fft(arrx, len(arrx))))
FILT = downsample_for_display(FILT, 20000)
plt.plot(FILT, 'r')
plt.show()
# N = 20000
# order = [1, 2, 3, 5, 10, 50, 100, 500, 1000, 2000]
# for o in order:
#     print o
#     filter = auto_regression(arrx, o)
#     FILT = -20*np.log10(np.abs(mfftw.real_fft(filter, N)))
#     plt.plot(FILT)
#     
# plt.show()

filter = auto_regression(arrx, 1)
arrx = slow_convolve(arrx, filter)

FILT = np.abs(mfftw.real_fft(arrx, len(arrx)))
FILT = downsample_for_display(FILT, 20000)
plt.plot(FILT, 'r')
plt.show()


# cProfile.runctx("auto_regression(arrx, 15000)", globals(), locals(), "Profile.prof")
# 
# s = pstats.Stats("Profile.prof")
# s.strip_dirs().sort_stats("time").print_stats()
# 
# cProfile.runctx("linear_predictor(arrx, 15000)", globals(), locals(), "Profile.prof")
# 
# s = pstats.Stats("Profile.prof")
# s.strip_dirs().sort_stats("time").print_stats()



# start_time = time.clock()
# x = auto_regression(arrx, 5000)
# print 'levinson durbin',  time.clock() - start_time
# 
# start_time = time.clock()
# y = np.hstack((np.array([1]), linear_predictor(arrx, 5000)))
# print 'matrix inversion', time.clock() - start_time





# FILT = np.log(1/np.abs(mfftw.real_fft(x, len(x)*100)))
# plt.plot(FILT, 'b')




# plt.show()
# 
# 
# print 'error', np.sum(np.square(x - y)/len(arrx))
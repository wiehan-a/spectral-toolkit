'''
Created on Sep 24, 2013

@author: Wiehan
'''

from data_processing.convolution import *
import numpy as np
import time

arrx = np.arange(0, 102000000, 1, dtype=np.float64)
arry = np.arange(0, 1200, 1, dtype=np.float64)

print len(arrx), len(arry)


#arrx = np.arange(0, 58, 0.5, dtype=np.float64)
#arry = np.array([7,1,8], dtype=np.float64)

# fast_convolve_fftw(arrx, arry)
# fast_convolve_fftw_w(arrx, arry)
start_time = time.clock()
#fast_convolve_fftw_w(arrx, arry)
x = fast_convolve_fftw_w(arrx, arry)
after_fast_convolve_fftw_w = time.clock()
print 'fast convolve fftw_w', after_fast_convolve_fftw_w - start_time

y = np.convolve(arrx, arry)[:-len(arry)+1]
after_npconvolve = time.clock()
print 'numpy convolve', after_npconvolve - after_fast_convolve_fftw_w

print 'Mean square error: ', np.sum(np.abs(x - y)/len(arrx))
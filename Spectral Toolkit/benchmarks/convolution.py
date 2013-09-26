'''
Created on Sep 24, 2013

@author: Wiehan
'''

from data_processing.convolution import *
import numpy as np
import time

arrx = np.arange(0, 92400000, 1, dtype=np.float64)
arry = np.arange(0, 500, 1, dtype=np.float64)

print len(arrx), len(arry)
fast_convolve_fftw_w(arrx, arry)

#arrx = np.arange(0, 58, 0.5, dtype=np.float64)
#arry = np.array([7,1,8], dtype=np.float64)

# fast_convolve_fftw(arrx, arry)

start_time = time.clock()

# slow_convolve(arrx, arry)
# after_slow_convolve = time.clock()
# print 'slow convolve', after_slow_convolve - start_time
 
# fast_convolve(arrx, arry)
# after_fast_convolve = time.clock()
# print 'fast convolve', after_fast_convolve - after_slow_convolve
 
# fast_convolve_fftw(arrx, arry)
# after_fast_convolve_fftw = time.clock()
# print 'fast convolve fftw', after_fast_convolve_fftw - after_fast_convolve

x = fast_convolve_fftw_w(arrx, arry)
after_fast_convolve_fftw_w = time.clock()
print 'fast convolve fftw_', after_fast_convolve_fftw_w - start_time

y = np.convolve(arrx, arry)[:-len(arry)+1]
after_npconvolve = time.clock()
print 'numpy convolve', after_npconvolve - after_fast_convolve_fftw_w

print 'Mean square error: ', np.sum(np.abs(x - y))/len(arrx)
'''
Created on Sep 24, 2013

@author: Wiehan
'''

from data_processing.convolution import *
import numpy as np
import time

arrx = np.arange(0, 10000000, 0.5, dtype=np.float64)
arry = np.array([7,1,8,5,5,4,7,7,1,7,1,8,5,5,4,7,7,1,7,1,8,5,5,4,7,7,1,7,1,8,5,5,4,7,7,1,7,1,8,5,5,4,7,7,1,7,1,8,5,5,4,7,7,1,7,1,8,5,5,4,7,7,1,7,1,8,5,5,4,7,7,1,7,1,8,5,5,4,7,7,1,7,1,8,5,5,4,7,7,1,7,1,8,5,5,4,7,7,1,7,1,8,5,5,4,7,7,1], dtype=np.float64)

#arrx = np.arange(0, 58, 0.5, dtype=np.float64)
#arry = np.array([7,1,8], dtype=np.float64)


start_time = time.clock()

slow_convolve(arrx, arry)
after_slow_convolve = time.clock()
print 'slow convolve', after_slow_convolve - start_time

fast_convolve_parallel(arrx, arry)
after_fast_convolve = time.clock()
print 'fast convolve', after_fast_convolve - after_slow_convolve

np.convolve(arrx, arry)[:-len(arry)+1]
after_npconvolve = time.clock()
print 'numpy convolve', after_npconvolve - after_fast_convolve
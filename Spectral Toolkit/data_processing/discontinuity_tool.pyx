'''
Created on Oct 2, 2013

@author: Wiehan
'''

import numpy as np
from data_processing.convolution import slow_convolve
cimport numpy as np

import matplotlib.pyplot as plt

from convolution import slow_convolve

from data_processing.display_friendly import *, downsample_for_display

def find_discontinuities(np.ndarray[np.float64_t] signal, double tolerance=10):
    '''
    
    '''
    
    differencer = np.array([1.0, -1])
    
    cdef np.ndarray[np.float64_t] differenced = slow_convolve(signal, differencer)
    cdef float std_dev = np.std(differenced)
    
    differenced = downsample_for_display(differenced)
    
    plt.plot(differenced)
    plt.show()
    
    
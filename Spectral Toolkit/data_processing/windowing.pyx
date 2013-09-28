'''
Created on Sep 27, 2013

@author: Wiehan
'''

import numpy as np
cimport numpy as np

import cython
cimport cython

from cython.parallel import prange
from libc.math cimport cos

@cython.boundscheck(False)
def apply_blackman(np.ndarray[dtype=np.float64_t] signal, inplace=True):
    '''
    Applies the Blackman window to the signal:
    
    w[n] = a0 - a1*cos(2*pi*n/(N-1)) +a2*cos(4*pi*n/(N-1))
    
    If inplace is False, a new buffer is allocated.
    '''
    cdef double alpha = 0.16
    
    cdef double a0 = (1 - alpha) / 2.0
    cdef double a1 = 0.5
    cdef double a2 = alpha / 2
    
    cdef int N = len(signal)
    
    print signal
    
    cdef np.ndarray[dtype = np.float64_t] out_buffer = signal
    if not inplace:
        out_buffer = np.empty(shape=(len(signal),), dtype=np.float64)
        
    cdef double inner_constant_1 = 2 * np.pi / (N - 1)
    cdef double inner_constant_2 = 4 * np.pi / (N - 1)
    
    cdef int idx = 0
    with nogil:
        for idx in prange(N, num_threads=8):
            out_buffer[idx] = signal[idx] * (a0 - a1 * cos(idx * inner_constant_1) + a2 * cos(idx * inner_constant_2))
            
    return out_buffer

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

@cython.boundscheck(False)
def apply_blackman_harris(np.ndarray[dtype=np.float64_t] signal, inplace=True):
    '''
    Applies the Blackman-Harris window to the signal:
    
    If inplace is False, a new buffer is allocated.
    '''
    
    cdef double a0 = 0.35875
    cdef double a1 = 0.48829
    cdef double a2 = 0.14128
    cdef double a3 = 0.01168
    
    cdef int N = len(signal)
    
    cdef np.ndarray[dtype = np.float64_t] out_buffer = signal
    if not inplace:
        out_buffer = np.empty(shape=(len(signal),), dtype=np.float64)
        
    cdef double inner_constant_1 = 2 * np.pi / (N - 1)
    cdef double inner_constant_2 = 4 * np.pi / (N - 1)
    cdef double inner_constant_3 = 6 * np.pi / (N - 1)
    
    cdef int idx = 0
    with nogil:
        for idx in prange(N, num_threads=8):
            out_buffer[idx] = signal[idx] * (a0 - a1 * cos(idx * inner_constant_1) + a2 * cos(idx * inner_constant_2) - a3 * cos(idx * inner_constant_3))
            
    return out_buffer

@cython.boundscheck(False)
def apply_flattop(np.ndarray[dtype=np.float64_t] signal, inplace=True):
    '''
    Applies the Blackman-Harris window to the signal:
    
    If inplace is False, a new buffer is allocated.
    '''
    
    cdef double a0 = 1
    cdef double a1 = -1.942604
    cdef double a2 = 1.340318
    cdef double a3 = -0.440811
    cdef double a4 = 0.043097
#     cdef double a0 = 0.21706
#     cdef double a1 = -0.42103
#     cdef double a2 = 0.28294
#     cdef double a3 = -0.07897
#     cdef double a4 = 0

    
    cdef int N = len(signal)
    
    cdef np.ndarray[dtype = np.float64_t] out_buffer = signal
    if not inplace:
        out_buffer = np.empty(shape=(len(signal),), dtype=np.float64)
        
    cdef double inner_constant_1 = 2 * np.pi / (N - 1)
    cdef double inner_constant_2 = 4 * np.pi / (N - 1)
    cdef double inner_constant_3 = 6 * np.pi / (N - 1)
    cdef double inner_constant_4 = 8 * np.pi / (N - 1)
    
    cdef int idx = 0
    with nogil:
        for idx in prange(N, num_threads=8):
            out_buffer[idx] = signal[idx] * (a0 + a1 * cos(idx * inner_constant_1) + a2 * cos(idx * inner_constant_2) + a3 * cos(idx * inner_constant_3) + a4 * cos(idx * inner_constant_4))
            
    return out_buffer

windows = {
                'Rectangular' : None,
                'Blackman' : apply_blackman,
                'Blackman-Harris' : apply_blackman_harris,
                'Flat-Top' : apply_flattop
          }

attenuation = {
                'Rectangular' : '13 dB', 
                'Blackman' : '58 dB',
                'Blackman-Harris' : '92 dB',
                'Flat-Top' : '90.2 dB'
          }

bw = {
                'Rectangular' : 0.89, 
                'Blackman' : 1.68,
                'Blackman-Harris' : 1.9,
                'Flat-Top' : 3.832
          }

overlap = {
                None: 0,
                apply_blackman: 0.5,
                apply_blackman_harris : 0.661,
                apply_flattop : 0.76,
          }

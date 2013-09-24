'''
Created on Sep 24, 2013

@author: Wiehan
'''

import numpy as np
import numpy.fft as fft
from Cython.Compiler.MemoryView import overlapping_utility
cimport numpy as np
cimport cython

from cython.parallel import prange
from cython.parallel cimport prange

@cython.boundscheck(False)
def slow_convolve(np.ndarray[np.float64_t, ndim=1] x not None,
                  np.ndarray[np.float64_t, ndim=1] h not None,
                  np.ndarray[np.float64_t, ndim=1] out_buffer=None):
    cdef Py_ssize_t n = 0, k = 0
    cdef np.float64_t tmp
    cdef Py_ssize_t x_len = len(x)
    cdef Py_ssize_t h_len = len(h)
    
    if out_buffer is None:
        out_buffer = np.empty(shape=(x_len,), dtype=x.dtype)
    
    with nogil:
        for n in prange(h_len, num_threads=8):
            for k in xrange(0, n + 1):
                out_buffer[n] += x[n - k] * h[k]
            
        for n in prange(h_len, x_len + 1, num_threads=8):
            for k in xrange(0, h_len):
                out_buffer[n] += x[n - k] * h[k]
        
    return out_buffer

def fast_convolve(np.ndarray[np.float64_t, ndim=1] x not None,
                  np.ndarray[np.float64_t, ndim=1] h not None,
                  np.ndarray[np.float64_t, ndim=1] out_buffer=None):
    
    '''
    Performs the fast convolution of the signals x and h, using the
    over-lap save method.
    
    y[n] = sum[k = 0:N](x[n-k]*h[k])
    '''
    
    cdef Py_ssize_t n_ = 0, k = 0
    cdef Py_ssize_t x_len_ = len(x)
    cdef Py_ssize_t M = len(h)
    cdef Py_ssize_t overlap = M - 1
    cdef Py_ssize_t N = 4 * overlap
    cdef Py_ssize_t step_size = N - overlap
    cdef np.ndarray[np.complex128_t, ndim = 1] H = fft.rfft(h, N)
    cdef Py_ssize_t position = 0
    
    
    if out_buffer is None:
        out_buffer = np.zeros(shape=(x_len_,), dtype=x.dtype)
    
    while position + N <= x_len_:
        yt = fft.irfft(H * fft.rfft(x[position : N + position]), N)
        out_buffer[position: step_size + position] = yt[M - 1 : N]
        position = position + step_size
    return out_buffer

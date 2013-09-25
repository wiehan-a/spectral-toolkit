'''
Created on Sep 24, 2013

@author: Wiehan
'''

import numpy as np
from Cython.Compiler.MemoryView import overlapping_utility
cimport numpy as np
import pyfftw
cimport pyfftw
cimport cython

from cython.parallel import prange
from cython.parallel cimport prange

@cython.boundscheck(False)
def slow_convolve(np.ndarray[np.float64_t, ndim=1] x not None,
                  np.ndarray[np.float64_t, ndim=1] h not None,
                  np.ndarray[np.float64_t, ndim=1] out_buffer=None):
    
    '''
    Performs the naive convolution of the signals x and h
    
    y[n] = sum[k = 0:N](x[n-k]*h[k])
    
    Useful for benchmarking purposes.
    
    '''
    
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
    cdef Py_ssize_t M = len(h)
    cdef Py_ssize_t N = int(2 ** (np.ceil(np.log2(4 * (M - 1)))))
    cdef Py_ssize_t L = N - M + 1
    cdef Py_ssize_t X = len(x)
    cdef Py_ssize_t out_start = 0
    cdef Py_ssize_t start = L - (M - 1) - 1
    cdef np.ndarray[np.complex128_t, ndim = 1] H_ = fft.rfft(h, N)
    
    if out_buffer is None:
        out_buffer = np.zeros(shape=(X,), dtype=x.dtype)
        
    first_block = np.hstack((np.zeros(M - 1), x[0:L]))
    out_buffer[out_start:out_start + L] = fft.irfft(H_ * fft.rfft(first_block, N))[M - 1:]
    out_start += L
    
    while start + N + 1 < X:
        first_block = x[start + 1:start + 1 + N]
        out_buffer[out_start:out_start + L] = fft.irfft(H_ * fft.rfft(first_block, N))[M - 1:]
        start += L
        out_start += L
    
    out_buffer[out_start:] = fft.irfft(H_ * fft.rfft(x[start + 1:], N)) [M - 1:M - 1 + len(out_buffer[out_start:])]
     
    return out_buffer

def fast_convolve_parallel(np.ndarray[np.float64_t, ndim=1] x not None,
                  np.ndarray[np.float64_t, ndim=1] h not None,
                  np.ndarray[np.float64_t, ndim=1] out_buffer=None):
    
    '''
    Performs the fast convolution of the signals x and h, using the
    over-lap save method.
    
    y[n] = sum[k = 0:N](x[n-k]*h[k])
    '''
    cdef Py_ssize_t M = len(h)
    cdef Py_ssize_t N = int(2 ** (np.ceil(np.log2(64 * (M - 1)))))
    cdef Py_ssize_t L = N - M + 1
    cdef Py_ssize_t X = len(x)
    cdef Py_ssize_t idx
    cdef np.ndarray[np.complex128_t, ndim = 1] H_ = fft.rfft(h, N)
    
    if out_buffer is None:
        out_buffer = np.zeros(shape=(X,), dtype=x.dtype)
        
    first_block = np.hstack((np.zeros(M - 1), x[0:L]))
    out_buffer[0:L] = fft.irfft(H_ * fft.rfft(first_block, N))[M - 1:]
    
    for idx in prange(L - (M - 1), X - N - 1, L, num_threads=8):
        out_buffer[idx + (M - 1): idx + (M - 1) + L] = fft.irfft(H_ * fft.rfft(x[idx:idx + N], N))[M - 1:]
    
    last = idx + (M-1) + L
    out_buffer[last:] = fft.irfft(H_ * fft.rfft(x[idx+L:], N)) [M - 1:M - 1 + len(out_buffer[last:])]
     
    return out_buffer

# def fast_convolve_bad(np.ndarray[np.float64_t, ndim=1] x not None,
#                   np.ndarray[np.float64_t, ndim=1] h not None,
#                   np.ndarray[np.float64_t, ndim=1] out_buffer=None):
#      
#     '''
#     Performs the fast convolution of the signals x and h, using the
#     over-lap save method.
#      
#     y[n] = sum[k = 0:N](x[n-k]*h[k])
#     '''
#      
#     cdef Py_ssize_t n_ = 0, k = 0
#     cdef Py_ssize_t x_len_ = len(x)
#     cdef Py_ssize_t M = len(h)
#     cdef Py_ssize_t overlap = M - 1
#     cdef Py_ssize_t N = 4 * overlap
#     cdef Py_ssize_t step_size = N - overlap
#     cdef np.ndarray[np.complex128_t, ndim = 1] H = fft.rfft(h, N)
#     cdef Py_ssize_t position = 0
#      
#      
#     if out_buffer is None:
#         out_buffer = np.zeros(shape=(x_len_,), dtype=x.dtype)
#      
#     while position + N <= x_len_:
#         yt = fft.irfft(H * fft.rfft(x[position : N + position]), N)
#         out_buffer[position: step_size + position] = yt[M - 1 : N]
#         position = position + step_size
#     return out_buffer

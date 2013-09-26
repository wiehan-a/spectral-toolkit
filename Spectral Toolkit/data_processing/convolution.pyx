'''
Created on Sep 24, 2013

@author: Wiehan
'''

import numpy as np
cimport numpy as np

import numpy.fft as fft

import pyfftw
import pyfftw.interfaces.numpy_fft as fftw

cimport cython
from fftw_wrapper.cfftw cimport * 

from cython.parallel import prange, parallel
from cython.parallel cimport prange, parallel

from libc.stdlib cimport abort, malloc, free

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

# def fast_convolve_fftw(np.ndarray[np.float64_t, ndim=1] x not None,
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
#     pyfftw.interfaces.cache.enable()
#     
#     cdef Py_ssize_t M = len(h)
#     cdef Py_ssize_t N = int(2 ** (np.ceil(np.log2(4 * (M - 1)))))
#     cdef Py_ssize_t L = N - M + 1
#     cdef Py_ssize_t X = len(x)
#     cdef Py_ssize_t idx
#     cdef np.ndarray[np.complex128_t, ndim = 1] H_ = fftw.rfft(h, N)
#      
#     if out_buffer is None:
#         out_buffer = np.zeros(shape=(X,), dtype=x.dtype)
#          
#     first_block = np.hstack((np.zeros(M - 1), x[0:L]))
#     out_buffer[0:L] = fftw.irfft(H_ * fftw.rfft(first_block, N))[M - 1:]
#      
#     for idx in xrange(L - (M - 1), X - N - 1, L):
#         out_buffer[idx + (M - 1): idx + (M - 1) + L] = fftw.irfft(H_ * fftw.rfft(x[idx:idx + N], N))[M - 1:]
#      
#     last = idx + (M - 1) + L
#     out_buffer[last:] = fftw.irfft(H_ * fftw.rfft(x[idx + L:], N)) [M - 1:M - 1 + len(out_buffer[last:])]
#       
#     return out_buffer

cdef void mult_dfts(size_t N, fftw_complex * A, fftw_complex * B) nogil:
    '''
        Perform the N-point complex multiplication a*b and store the result in b
    '''
    cdef int idx
    cdef double a, b, c, d
    for idx in xrange(N):
        a = A[idx][0]; b = A[idx][1]
        c = B[idx][0]; d = B[idx][1]
        B[idx][0] = a * c - b * d
        B[idx][1] = b * c + a * d

def fast_convolve_fftw_w(np.ndarray[np.float64_t, ndim=1] x not None,
                  np.ndarray[np.float64_t, ndim=1] h not None,
                  np.ndarray[np.float64_t, ndim=1] out_buffer=None):
    
    '''
    Performs the fast convolution of the signals x and h, using the
    over-lap save method.
    
    The FFTW3 library is invoked and chunks are executed in parallel
    
    y[n] = sum[k = 0:N](x[n-k]*h[k])
    '''
    cdef Py_ssize_t M = len(h)
    cdef Py_ssize_t X = len(x)
    cdef Py_ssize_t L = 2**int((np.log2(M*16))) + 1
    cdef Py_ssize_t N = L + M - 1

    cdef Py_ssize_t out_start = 0
    cdef Py_ssize_t start = L - (M - 1) - 1
    cdef double * input_buffer = < double *> x.data
    cdef np.ndarray[np.complex128_t, ndim = 1] H_ = np.zeros(shape=(N,), dtype=np.complex128)
    cdef np.ndarray[np.float64_t, ndim = 1] h_zero_padded = np.hstack((h, np.zeros(N - M)))
    
    # calculate FFT of h
    cdef fftw_plan forward_plan = fftw_plan_dft_r2c_1d(N, < double *> h_zero_padded.data, < fftw_complex *> H_.data, FFTW_PRESERVE_INPUT | FFTW_MEASURE)
    fftw_execute(forward_plan)
    
    if out_buffer is None:
        out_buffer = np.empty(shape=(X,), dtype=np.float64)
        
    cdef double * output_data = < double *> out_buffer.data
    
    cdef np.ndarray[np.float64_t, ndim = 1] first_block = np.hstack((np.zeros(M - 1), x[0:L]))
    cdef fftw_complex * outblock = < fftw_complex *> fftw_alloc_complex(N / 2 + 1)
    fftw_execute_dft_r2c(forward_plan, < double *> first_block.data, outblock)
    
    mult_dfts(N / 2 + 1, < fftw_complex *> H_.data, outblock)
    
    cdef int idx3 = 0
   
    
    cdef double * real_outblock = < double *> fftw_alloc_real(N)
    cdef fftw_plan backward_plan = fftw_plan_dft_c2r_1d(N, outblock, real_outblock, FFTW_MEASURE)

    fftw_execute(backward_plan)
    

    for idx3 in xrange(L):
        output_data[idx3] = real_outblock[M - 1 + idx3] / N
    
    cdef int idx, idx2
    cdef fftw_complex * local_out_block
    cdef double * local_real_out_block

    with nogil, parallel(num_threads=8):
        local_out_block = < fftw_complex *> fftw_alloc_complex(N / 2 + 1)
        local_real_out_block = < double *> fftw_alloc_real(N)
        
        for idx in prange(L - (M - 1), X - 1, L):
            fftw_execute_dft_r2c(forward_plan, input_buffer + idx, local_out_block)
            mult_dfts(N / 2 + 1, < fftw_complex *> H_.data, local_out_block)
            fftw_execute_dft_c2r(backward_plan, local_out_block, local_real_out_block)
            for idx2 in xrange(M - 1, N):
                output_data[idx + idx2] = local_real_out_block[idx2] / N
       
    cdef int last = idx + L
    cdef np.ndarray[np.float64_t, ndim = 1] last_block

    if last < X:
        last_block = np.hstack((x[last:], np.zeros(shape=(N - (X - last),), dtype=np.float64)))

        local_out_block = < fftw_complex *> fftw_alloc_complex(N / 2 + 1)
        fftw_execute_dft_r2c(forward_plan, < double *> last_block.data, local_out_block)
        mult_dfts(N / 2 + 1, < fftw_complex *> H_.data, local_out_block)
        local_real_out_block = < double *> fftw_alloc_real(N)
        fftw_execute_dft_c2r(backward_plan, local_out_block, local_real_out_block)
        
        idx2 = 0
        for idx2 in xrange(M - 1, M - 1 + X % L):
             output_data[last + idx2] = local_real_out_block[idx2] / N
        
    return out_buffer
    
#     fftw_destroy_plan(plan)
#     fftw_free(H_)

# def fast_convolve_fftw_parallel(np.ndarray[np.float64_t, ndim=1] x not None,
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
#     pyfftw.interfaces.cache.enable()
#      
#     cdef Py_ssize_t M = len(h)
#     cdef Py_ssize_t N = int(2 ** (np.ceil(np.log2(64 * (M - 1)))))
#     cdef Py_ssize_t L = N - M + 1
#     cdef Py_ssize_t X = len(x)
#     cdef Py_ssize_t idx
#     cdef np.ndarray[np.complex128_t, ndim = 1] H_ = fftw.rfft(h, N)
#       
#     if out_buffer is None:
#         out_buffer = np.zeros(shape=(X,), dtype=x.dtype)
#           
#     first_block = np.hstack((np.zeros(M - 1), x[0:L]))
#     out_buffer[0:L] = fftw.irfft(H_ * fftw.rfft(first_block, N))[M - 1:]
#      
#     with nogil:
#         for idx in prange(L - (M - 1), X - N - 1, L):
#             tmp = fftw.irfft(H_) # fftw.rfft(x[idx:idx + N], N))
#             #[M - 1:]
#             #out_buffer[idx + (M - 1): idx + (M - 1) + L] = 
#       
#     last = idx + (M-1) + L
#     out_buffer[last:] = fftw.irfft(H_ * fftw.rfft(x[idx+L:], N)) [M - 1:M - 1 + len(out_buffer[last:])]
#        
#     return out_buffer

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

'''
Created on Sep 24, 2013

@author: Wiehan
'''

import numpy as np
from utils import get_cpu_count
cimport numpy as np

import numpy.fft as fft

cimport cython
from fftw_wrapper.cfftw cimport * 
from fftw_wrapper.fftw_py import real_fft, inverse_real_fft

from cython.parallel import prange, parallel
from cython.parallel cimport prange, parallel

from libc.stdlib cimport abort, malloc, free
from libc.string cimport memcpy


@cython.boundscheck(False)
def slow_convolve(np.ndarray[np.float64_t, ndim=1] x not None,
                  np.ndarray[np.float64_t, ndim=1] h not None,
                  np.ndarray[np.float64_t, ndim=1] out_buffer=None, delay=0):
    
    '''
    Performs the naive convolution of the signals x and h
    
    y[n] = sum[k = 0:N](x[n-k]*h[k])
    
    Useful for benchmarking purposes.
    
    '''
    
    cdef int n = 0, k = 0
    cdef np.float64_t tmp
    cdef int x_len = len(x) + delay
    cdef int h_len = len(h)
    
    cdef np.ndarray[np.float64_t] t_buf = np.zeros(shape=(x_len,), dtype=x.dtype)
    memcpy(& t_buf.data[0], & x.data[0], len(x) * sizeof(double))
    x = t_buf
    
    if out_buffer is None:
        out_buffer = np.zeros(shape=(x_len,), dtype=x.dtype)
    
    cdef int CPU_COUNT = get_cpu_count()
    if CPU_COUNT == 1:
        for n in xrange(h_len):
                for k in xrange(0, n + 1):
                    out_buffer[n] += x[n - k] * h[k]
                
        for n in xrange(h_len, x_len):
            for k in xrange(0, h_len):
                out_buffer[n] += x[n - k] * h[k]
    else:
        with nogil:
            for n in prange(h_len, num_threads=CPU_COUNT):
                for k in xrange(0, n + 1):
                    out_buffer[n] += x[n - k] * h[k]
                
            for n in prange(h_len, x_len, num_threads=CPU_COUNT):
                for k in xrange(0, h_len):
                    out_buffer[n] += x[n - k] * h[k]
        
    return out_buffer[delay:]

# @cython.boundscheck(False)
# def fast_convolve(np.ndarray[np.float64_t, ndim=1] x not None,
#                   np.ndarray[np.float64_t, ndim=1] h not None,
#                   np.ndarray[np.float64_t, ndim=1] out_buffer=None, delay=0):
#     
#     '''
#     Performs the fast convolution of the signals x and h, using the
#     over-lap save method.
#     
#     y[n] = sum[k = 0:N](x[n-k]*h[k])
#     '''
#     cdef int M = len(h)
#     cdef int N = int(2 ** (np.ceil(np.log2(4 * (M - 1)))))
#     cdef int L = N - M + 1
#     cdef int X = len(x) + delay
#     print N, X
# 
#     cdef Py_ssize_t out_start = 0
#     cdef Py_ssize_t start = L - (M - 1) - 1
#     cdef np.ndarray[np.complex128_t, ndim = 1] H_ = fft.rfft(h, N)
#     
# 
#     
#     if out_buffer is None:
#         out_buffer = np.zeros(shape=(X,), dtype=x.dtype)
#         
#     first_block = np.hstack((np.zeros(M - 1), x[0:L]))
#     out_buffer[out_start:out_start + L] = fft.irfft(H_ * fft.rfft(first_block, N))[M - 1:]
#     out_start += L
#     
#     while start + N + 1 < X:
#         first_block = x[start + 1:start + 1 + N]
#         out_buffer[out_start:out_start + L] = fft.irfft(H_ * fft.rfft(first_block, N))[M - 1:]
#         start += L
#         out_start += L
#     
#     out_buffer[out_start:] = fft.irfft(H_ * fft.rfft(x[start + 1:], N)) [M - 1:M - 1 + len(out_buffer[out_start:])]
#      
#     return out_buffer[delay:]

@cython.boundscheck(False)
cdef void mult_dfts(int N, fftw_complex * A, fftw_complex * B) nogil:
    '''
        Perform the N-point complex multiplication a*b and store the result in b
    '''
    cdef int idxx
    cdef double a, b, c, d
    for idxx in xrange(N):
        a = A[idxx][0]; b = A[idxx][1]
        c = B[idxx][0]; d = B[idxx][1]
        B[idxx][0] = a * c - b * d
        B[idxx][1] = b * c + a * d
        
@cython.cdivision(True)
@cython.boundscheck(False)
def fast_convolve_fftw_w(np.ndarray[np.float64_t, ndim=1] x not None,
                  np.ndarray[np.float64_t, ndim=1] h not None,
                  np.ndarray[np.float64_t, ndim=1] out_buffer=None, delay=0, prev_block=None):
     
    '''
    Performs the fast convolution of the signals x and h, using the
    overlap save method.
     
    The FFTW3 library is invoked and chunks are executed in parallel
     
    y[n] = sum[k = 0:N](x[n-k]*h[k])
     
    TODO: check for failure conditions and handle them more gracefully
    '''
     
    cdef int M = len(h)
    cdef int X = len(x) + delay
    
    if prev_block is None:
        prev_block = np.zeros(M - 1)
        
    assert len(prev_block) == M - 1
    
    #print delay, M
     
    cdef int N = 2 ** int((np.log2(M * 4)))
    cdef int L = N - M + 1
     
    x = np.ascontiguousarray(np.hstack((x, np.zeros(delay))))
 
    cdef int out_start = 0
    cdef int start = L - (M - 1) - 1
     
    cdef np.ndarray[np.complex128_t, ndim = 1] H_ = real_fft(h, N)
     
    if out_buffer is None:
        out_buffer = np.zeros(shape=(X,), dtype=np.float64)
         
    cdef double * output_data = < double *> out_buffer.data
     
    cdef np.ndarray[np.float64_t, ndim = 1] first_block = np.hstack((prev_block, x[0:L]))
    cdef np.ndarray[np.complex128_t, ndim = 1] outblock = real_fft(first_block, N)
    mult_dfts(N / 2 + 1, < fftw_complex *> H_.data, < fftw_complex *> outblock.data)
    cdef np.ndarray[np.float64_t, ndim = 1] real_outblock = inverse_real_fft(outblock, N)
     
    cdef int idx3 = 0
    for idx3 in xrange(L):
        output_data[idx3] = real_outblock[M - 1 + idx3] / N
     
    cdef int idx, idx2     
    cdef int last = L - (M - 1) + L * int(np.floor((X - (X % L) - (L - (M - 1))) / L))
    
    cdef double * sli = <double *> x.data
    cdef double * local_
    cdef fftw_complex * local_out_block
    cdef double * local_real_out_block
    cdef fftw_plan forward_plan
    
    local_out_block = < fftw_complex *> fftw_alloc_complex(N/2+1)
    local_real_out_block = < double *> fftw_alloc_real(N)
    forward_plan = fftw_plan_dft_r2c_1d(N, local_real_out_block, local_out_block, FFTW_MEASURE)
    backward_plan = fftw_plan_dft_c2r_1d(N, local_out_block, local_real_out_block, FFTW_MEASURE)
    
    cdef int CPU_COUNT = get_cpu_count()
    if CPU_COUNT == 1:
        local_out_block = < fftw_complex *> fftw_alloc_complex(N/2+1)
        local_real_out_block = < double *> fftw_alloc_real(N)
          
        for idx in xrange(L - (M - 1), last, L):
            local_ = & sli[idx]
            memcpy(local_real_out_block, local_, N * sizeof(double))
            fftw_execute_dft_r2c(forward_plan, local_real_out_block, local_out_block)
            mult_dfts(N / 2 + 1, < fftw_complex *> H_.data, local_out_block)
            fftw_execute_dft_c2r(backward_plan, local_out_block, local_real_out_block)
            
            for idx2 in xrange(M - 1, N):
                output_data[idx + idx2] = local_real_out_block[idx2] / N
  
        fftw_free(local_out_block)
        fftw_free(local_real_out_block)
    else:
        with nogil, parallel(num_threads=CPU_COUNT):
             
            local_out_block = < fftw_complex *> fftw_alloc_complex(N/2+1)
            local_real_out_block = < double *> fftw_alloc_real(N)
              
            for idx in prange(L - (M - 1), last, L):
                local_ = & sli[idx]
                memcpy(local_real_out_block, local_, N * sizeof(double))
                fftw_execute_dft_r2c(forward_plan, local_real_out_block, local_out_block)
                mult_dfts(N / 2 + 1, < fftw_complex *> H_.data, local_out_block)
                fftw_execute_dft_c2r(backward_plan, local_out_block, local_real_out_block)
                
                for idx2 in xrange(M - 1, N):
                    output_data[idx + idx2] = local_real_out_block[idx2] / N
      
            fftw_free(local_out_block)
            fftw_free(local_real_out_block)
    
    fftw_destroy_plan(forward_plan)
    fftw_destroy_plan(backward_plan)
    
    cdef np.ndarray[np.complex128_t, ndim = 1] local_out_block_
    cdef np.ndarray[np.float64_t, ndim = 1] local_real_out_block_
  
    if last < X:
        local_out_block_ = real_fft(x[last:], N)
        mult_dfts(N / 2 + 1, < fftw_complex *> H_.data, < fftw_complex *> local_out_block_.data)
        local_real_out_block_ = inverse_real_fft(local_out_block_, N)
            
        idx2 = 0
        for idx2 in xrange(M - 1, M - 1 + X % L):
            output_data[last + idx2] = local_real_out_block_[idx2] / N
           
    return out_buffer[delay:]

# @cython.cdivision(True)
# @cython.boundscheck(False)
# def fast_downsample(np.ndarray[np.float64_t, ndim=1] x not None,
#                   np.ndarray[np.float64_t, ndim=1] h not None, int factor not None,
#                   np.ndarray[np.float64_t, ndim=1] out_buffer=None, delay=0):
#      
#     '''
# 
#     '''
#      
#     cdef int M = len(h)
#     cdef int X = len(x) + delay
#     
#     print delay, M
#      
#     cdef int N = 2 ** int((np.log2(M * 4)))
#     cdef int L = N - M + 1
#     
#     cdef int K = N/factor
#      
#     x = np.hstack((x, np.zeros(delay)))
#  
#     cdef int out_start = 0
#     cdef int start = L - (M - 1) - 1
#      
#     cdef np.ndarray[np.complex128_t, ndim = 1] H_ = real_fft(h, N)
#      
#     print len(H_), N
#      
#     if out_buffer is None:
#         out_buffer = np.zeros(shape=(X,), dtype=np.float64)
#          
#     cdef double * output_data = < double *> out_buffer.data
#      
#     cdef np.ndarray[np.float64_t, ndim = 1] first_block = np.hstack((np.zeros(M - 1), x[0:L]))
#     cdef np.ndarray[np.complex128_t, ndim = 1] outblock = real_fft(first_block, N)
#     mult_dfts(N / 2 + 1, < fftw_complex *> H_.data, < fftw_complex *> outblock.data)
#     cdef np.ndarray[np.float64_t, ndim = 1] real_outblock = inverse_real_fft(outblock, N)
#      
#     cdef int idx3 = 0
#     for idx3 in xrange(L):
#         output_data[idx3] = real_outblock[M - 1 + idx3] / N
#      
#     cdef int idx, idx2
#     cdef np.ndarray[np.complex128_t, ndim = 1] local_out_block
#     cdef np.ndarray[np.float64_t, ndim = 1] local_real_out_block
#      
#     cdef int last = L - (M - 1) + L * int(np.floor((X - (X % L) - (L - (M - 1))) / L))
#      
# #     with nogil, parallel(num_threads=8):  
#     for idx in xrange(L - (M - 1), last, L):
#         local_out_block = real_fft(x[idx:idx + N], N)
#         mult_dfts(N / 2 + 1, < fftw_complex *> H_.data, < fftw_complex *> local_out_block.data)
#         local_real_out_block = inverse_real_fft(local_out_block, N)
#         for idx2 in xrange(M - 1, N):
#             assert idx + idx2 < X
#             output_data[idx + idx2] = local_real_out_block[idx2] / N
#     
#   
#     if last < X:
#         local_out_block = real_fft(x[last:], N)
#         mult_dfts(N / 2 + 1, < fftw_complex *> H_.data, < fftw_complex *> local_out_block.data)
#         local_real_out_block = inverse_real_fft(local_out_block, N)
#             
#         idx2 = 0
#         for idx2 in xrange(M - 1, M - 1 + X % L):
#             output_data[last + idx2] = local_real_out_block[idx2] / N
#            
#      
#     return out_buffer[delay:]

# @cython.cdivision(True)
# @cython.boundscheck(False)
# def fast_convolve_fftw_w(np.ndarray[np.float64_t, ndim=1] x not None,
#                   np.ndarray[np.float64_t, ndim=1] h not None,
#                   np.ndarray[np.float64_t, ndim=1] out_buffer=None, delay=0):
#      
#     '''
#     Performs the fast convolution of the signals x and h, using the
#     overlap save method.
#      
#     The FFTW3 library is invoked and chunks are executed in parallel
#      
#     y[n] = sum[k = 0:N](x[n-k]*h[k])
#      
#     TODO: check for failure conditions and handle them more gracefully
#     '''
#      
#     cdef int M = len(h)
#     cdef int X = len(x) + delay
#      
#     cdef int N = 2 ** int((np.log2(M * 4)))
#     cdef int L = N - M + 1
#      
#     cdef np.ndarray[np.float64_t] t_buf = np.zeros(shape=(X,), dtype=x.dtype)
#     memcpy(& t_buf.data[0], & x.data[0], len(x) * sizeof(double))
#     x = None
#  
#     cdef int out_start = 0
#     cdef int start = L - (M - 1) - 1
#     cdef double * input_buffer = < double *> t_buf.data
#     cdef np.ndarray[np.complex128_t, ndim = 1] H_ = np.zeros(shape=(N,), dtype=np.complex128)
#     cdef np.ndarray[np.float64_t, ndim = 1] h_zero_padded = np.zeros(shape=(N,), dtype=np.float64)
#          
#     # create the forward plan. this clobbers h_zero_padded
#     cdef fftw_plan forward_plan = fftw_plan_dft_r2c_1d(N, < double *> h_zero_padded.data, < fftw_complex *> H_.data, FFTW_MEASURE)
#     memcpy(& h_zero_padded.data[0], & h.data[0], M * sizeof(double))
#     fftw_execute(forward_plan)
#      
#     if out_buffer is None:
#         out_buffer = np.zeros(shape=(X,), dtype=np.float64)
#          
#     cdef double * output_data = < double *> out_buffer.data
#      
#     cdef np.ndarray[np.float64_t, ndim = 1] first_block = np.hstack((np.zeros(M - 1), t_buf[0:L]))
#     cdef fftw_complex * outblock = < fftw_complex *> fftw_alloc_complex(N / 2 + 1)
#     cdef double * real_outblock = < double *> fftw_alloc_real(N)
#     cdef fftw_plan backward_plan = fftw_plan_dft_c2r_1d(N, outblock, real_outblock, FFTW_MEASURE)
#     fftw_execute_dft_r2c(forward_plan, < double *> first_block.data, outblock)
#      
#     mult_dfts(N / 2 + 1, < fftw_complex *> H_.data, outblock)
#      
#     cdef int idx3 = 0
#      
#  
#      
#      
#      
#  
#     fftw_execute(backward_plan)
#      
#  
#     for idx3 in xrange(L):
#         output_data[idx3] = real_outblock[M - 1 + idx3] / N
#      
#     cdef int idx, idx2
#     cdef fftw_complex * local_out_block
#     cdef double * local_real_out_block
#     cdef int last = L - (M - 1) + L * int(np.floor((X - (X % L) - (L - (M - 1))) / L))
#     
#     with nogil, parallel(num_threads=8):
#         local_out_block = < fftw_complex *> fftw_alloc_complex(N)
#         local_real_out_block = < double *> fftw_alloc_real(N)  
#         for idx in prange(L - (M - 1), last, L):
#              
#             memcpy(local_real_out_block, & input_buffer[idx], N * sizeof(double))
#             fftw_execute_dft_r2c(forward_plan, local_real_out_block , local_out_block)
#             mult_dfts(N / 2 + 1, < fftw_complex *> H_.data, local_out_block)
#             fftw_execute_dft_c2r(backward_plan, local_out_block, local_real_out_block)
#             for idx2 in xrange(M - 1, N):
#                 output_data[idx + idx2] = local_real_out_block[idx2] / N
#                  
#         # Destroy thread, local buffers:
#         fftw_free(local_out_block)
#         fftw_free(local_real_out_block)
#  
#     cdef np.ndarray[np.float64_t, ndim = 1] last_block
#   
# #     print '***', last, X
#     if last < X:
# #         print "I HAPPEN"
#         last_block = np.hstack((t_buf[last:], np.zeros(shape=(N - (X - last),), dtype=np.float64)))
#    
#         local_out_block = < fftw_complex *> fftw_alloc_complex(N / 2 + 1)
#         fftw_execute_dft_r2c(forward_plan, < double *> last_block.data, local_out_block)
#         mult_dfts(N / 2 + 1, < fftw_complex *> H_.data, local_out_block)
#         local_real_out_block = < double *> fftw_alloc_real(N)
#         fftw_execute_dft_c2r(backward_plan, local_out_block, local_real_out_block)
#            
#         idx2 = 0
#         for idx2 in xrange(M - 1, M - 1 + X % L):
#             output_data[last + idx2] = local_real_out_block[idx2] / N
#            
#         fftw_free(local_out_block)
#         fftw_free(local_real_out_block)
#          
#     fftw_destroy_plan(forward_plan)
#     fftw_destroy_plan(backward_plan)
#     fftw_free(outblock)
#     fftw_free(real_outblock)
#      
#     return out_buffer[delay:]

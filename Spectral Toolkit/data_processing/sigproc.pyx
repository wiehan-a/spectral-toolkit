
'''
Created on Aug 15, 2013

@author: Wiehan
'''
from __future__ import division
import numpy as np

cimport numpy as np
cimport cython

from cython.parallel import prange
from fftw_wrapper.cfftw cimport * 
import fftw_wrapper.fftw_py as mfftw

from libc.string cimport memcpy

@cython.boundscheck(False)
def auto_correlation(np.ndarray[dtype=np.float64_t] signal, maximum_lag=3):
    '''
    Estimates the autocorrelation sequence Rxx[n] for n=0,1..,maximum_lag
    '''
    cdef np.ndarray[dtype = np.float64_t] estimate = np.empty(maximum_lag + 1, dtype=np.float64)
    cdef int N = len(signal) - 1
    cdef int m
    for m in xrange(len(estimate)):
        sl1 = signal[0:N + 1 - m]
        sl2 = signal[m:N + 1]
        estimate[m] = np.dot(sl1, sl2)
    
    return estimate / (2 * N + 1)

cdef void abs_squared(int N, fftw_complex * A) nogil:
    '''
        Calculates the magnitude squared of A and stores the result in B
    '''
    cdef int idxx
    with nogil:
        for idxx in prange(N, num_threads=8):
            A[idxx][0] = A[idxx][0] * A[idxx][0] + A[idxx][1] * A[idxx][1]
            A[idxx][1] = 0

@cython.boundscheck(False)
def auto_correlation_fft(np.ndarray[dtype=np.float64_t] signal, maximum_lag=3):
    '''
    Estimates the autocorrelation sequence Rxx[n] for n=0,1..,maximum_lag
    '''
    cdef np.ndarray[dtype = np.float64_t] estimate = np.empty(maximum_lag + 1, dtype=np.float64)
    cdef int N = len(signal) - 1
    cdef int m
    
    cdef np.ndarray[dtype = np.float64_t] working_space = np.ascontiguousarray(np.hstack((signal, np.zeros(shape=(maximum_lag), dtype=np.float64))), dtype=np.float64)
    cdef np.ndarray[np.complex128_t] DFT = mfftw.real_fft(working_space, len(working_space))
    abs_squared(int(len(working_space) / 2 + 1), < fftw_complex *> & DFT.data[0])
    
    cdef np.ndarray[dtype = np.float64_t] x = mfftw.inverse_real_fft(DFT, len(working_space)) / (2 * N + 1)

    cdef int idx
    for idx in xrange(maximum_lag + 1):
        estimate[idx] = x[idx]
    
    return estimate

def levinson_durbin_recursion(np.ndarray[dtype=np.float64_t] R):
    '''
    Performs Levinson-Durbin recursion to solve the Yule-Walker equations
    for an AR process. The process is assumed to be real.
    
    R - autocorrelation vector
    
    returns the coefficients [1, a1, a2 .. am]
    '''
    cdef int order = len(R) - 1
    cdef np.ndarray[dtype = np.float64_t] solution = np.empty(shape=(order + 1), dtype=np.float64)
    cdef np.ndarray[dtype = np.float64_t] solution_x = np.empty(shape=(order + 1), dtype=np.float64)
    
    solution[0] = 1
    solution[1] = -1 * R[1] / R[0]    
    solution_x[0] = 1
    
    cdef int idx, idx2, t
    cdef double numerator, denominator
    for idx in xrange(2, order + 1):
        numerator = R[idx]
        denominator = R[0]
        for idx2 in xrange(1, idx):
            t = idx - idx2
            numerator += solution[idx2] * R[t]
            denominator += solution[t] * R[t]
            
        solution_x[idx] = -1 * numerator / denominator
        with nogil:
            for idx2 in prange(1, idx, num_threads=8):
                solution_x[idx2] = solution[idx2] + solution_x[idx] * solution[idx - idx2]
        
        solution, solution_x = solution_x, solution
        
    return solution

def auto_regression(signal, order=3):
    R = auto_correlation_fft(signal, order)
    return levinson_durbin_recursion(R)
    
    

def get_auto_corr_matrix(signal, order=3):
    R = auto_correlation_fft(signal, order)
    R_ = np.hstack((R[1:][::-1],R))
    auto_corr_matrix = np.vstack((R_[-1*i+order:2*order-1*i] for i in xrange(order)))
    return R, auto_corr_matrix
 
def linear_predictor(signal, order=3):
    R, auto_corr_matrix = get_auto_corr_matrix(signal, order)
    a = np.linalg.solve(auto_corr_matrix, -1*R[1:])
    #print a
    #b0s = np.dot(R, np.hstack((np.array([1]), a)))
    #print b0s
     
    return a
# 
# def p_do(idx, signal, order, a):
#     return np.abs(signal[idx] + np.dot(a, signal[idx-order:idx]))
# 
# @cython.boundscheck(False) # turn off bounds-checking for entire function
# def predict_signal(np.ndarray[DTYPE_t, ndim=1] signal, order=3):
#     a = linear_predictor(signal, order)[::-1]
#     print "done with lin predict estim"
#     N = len(signal)
#     cdef np.ndarray[DTYPE_t, ndim=1] pred = np.zeros(N)
#     
#     for idx in xrange(order, N):
#         pred[idx] = np.abs(signal[idx] + np.dot(a, signal[idx-order:idx]))
#         
#     print "done with error estim"
#     #pred[order:] = Parallel(n_jobs=4, verbose=10)(delayed(p_do)(idx, signal, order, a) for idx in xrange(order, N))
#     
# 
#     #plt.plot(pred, 'r')
#     #plt.plot(np.abs(sig.lfilter([1, 0, -16, 0,  16, 0, -1], [-16], signal)), 'b')
#     #plt.show()
#     
#     return pred
#     
    

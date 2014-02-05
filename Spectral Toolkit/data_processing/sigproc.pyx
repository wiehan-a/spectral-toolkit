
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
def auto_correlation(signal, maximum_lag=3):
    '''
    Estimates the autocorrelation sequence Rxx[n] for n=0,1..,maximum_lag
    '''
    cdef np.ndarray[dtype = np.float64_t] estimate = np.empty(maximum_lag + 1, dtype=np.float64)
    cdef int N = len(signal) - 1
    cdef int m
    for m in xrange(len(estimate)):
        sl1 = signal[0:N + 1 - m]
        sl2 = signal[m:N + 1]
        print len(sl1), len(sl2)
        estimate[m] = np.dot(sl1, sl2)
    
    return estimate / (2 * N + 1)

@cython.boundscheck(False)
cdef void abs_squared(int N, fftw_complex * A) nogil:
    '''
        Calculates the magnitude squared of A and stores the result in B
    '''
    cdef int idxx
    #with nogil:
    for idxx in xrange(N):
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
    cdef int len_working_space = len(working_space)
    cdef np.ndarray[np.complex128_t] DFT = mfftw.real_fft(working_space, len(working_space))
    working_space = None
    abs_squared(int(len_working_space / 2 + 1), < fftw_complex *> & DFT.data[0])
    
    working_space = mfftw.inverse_real_fft(DFT, len_working_space) / (N + 1) / (N + 1)

    cdef int idx
    for idx in xrange(maximum_lag + 1):
        estimate[idx] = working_space[idx]
    
    del working_space
    
    return estimate

@cython.boundscheck(False)
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
#        with nogil:
        for idx2 in xrange(1, idx):
            solution_x[idx2] = solution[idx2] + solution_x[idx] * solution[idx - idx2]
        
        solution, solution_x = solution_x, solution
        
    return solution

@cython.boundscheck(False)
def auto_regression(signal, order=3):
    corr_func = auto_correlation_fft
    if order < 10:
        corr_func = auto_correlation
    R = corr_func(signal, order)
    a = levinson_durbin_recursion(R)
    
    return a, np.dot(R, a)
    
    
@cython.boundscheck(False)
def get_auto_corr_matrix(signal, order=3):
    R = auto_correlation_fft(signal, order)
    R_ = np.hstack((R[1:][::-1], R))
    auto_corr_matrix = np.vstack((R_[-1 * i + order:2 * order - 1 * i] for i in xrange(order)))
    return R, auto_corr_matrix

@cython.boundscheck(True)
def do_prediction(np.ndarray[dtype=np.float64_t] signal, np.ndarray[dtype=np.float64_t] predictor, sections):
    cdef int order = len(predictor)
    cdef int start_idx = 0
    cdef int idx = 0
    cdef int idx2 = 0
    for section in sections:
        for idx in xrange(max(0, section[0]-3), min(len(signal), section[1]+3)):
            max_back = min(idx, order)
            signal[idx] = 0
            for idx2 in xrange(1, max_back):
                signal[idx] -= signal[idx - idx2] * predictor[idx2]
 
@cython.boundscheck(False)
def linear_predictor(signal, order=3):
    R, auto_corr_matrix = get_auto_corr_matrix(signal, order)
    a = np.linalg.solve(auto_corr_matrix, -1 * R[1:])
    # print a
    # b0s = np.dot(R, np.hstack((np.array([1]), a)))
    # print b0s
     
    return a     
    

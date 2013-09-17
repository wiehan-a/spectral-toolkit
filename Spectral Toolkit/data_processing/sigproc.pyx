'''
Created on Aug 15, 2013

@author: Wiehan
'''
from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal.signaltools import lfilter
import scipy.signal as sig
from numpy.core.numeric import ndarray

cimport numpy as np
cimport cython


DTYPE = np.float64
# "ctypedef" assigns a corresponding compile-time type to DTYPE_t. For
# every type in the numpy module there's a corresponding compile-time
# type with a _t-suffix.
ctypedef np.float64_t DTYPE_t

def auto_corr(signal, maximum_lag=3):
    estimate = np.zeros(maximum_lag+1)
    N = len(signal) - 1
    for m in xrange(len(estimate)):
        sl1 = signal[0:N+1-m]
        sl2 = signal[m:N+1]
        estimate[m] = np.dot(sl1, sl2)
    
    return estimate/(2*N+1)

def get_auto_corr_matrix(signal, order=3):
    R = auto_corr(signal, order)
    R_ = np.hstack((R[1:][::-1],R))
    auto_corr_matrix = np.vstack((R_[-1*i+order:2*order-1*i] for i in xrange(order)))
    return R, auto_corr_matrix

def linear_predictor(signal, order=3):
    R, auto_corr_matrix = get_auto_corr_matrix(signal, order)
    a = np.linalg.solve(auto_corr_matrix, -1*R[1:])
    #print a
    b0s = np.dot(R, np.hstack((np.array([1]), a)))
    #print b0s
    
    return a

def p_do(idx, signal, order, a):
    return np.abs(signal[idx] + np.dot(a, signal[idx-order:idx]))

@cython.boundscheck(False) # turn off bounds-checking for entire function
def predict_signal(np.ndarray[DTYPE_t, ndim=1] signal, order=3):
    a = linear_predictor(signal, order)[::-1]
    print "done with lin predict estim"
    N = len(signal)
    cdef np.ndarray[DTYPE_t, ndim=1] pred = np.zeros(N)
    
    for idx in xrange(order, N):
        pred[idx] = np.abs(signal[idx] + np.dot(a, signal[idx-order:idx]))
        
    print "done with error estim"
    #pred[order:] = Parallel(n_jobs=4, verbose=10)(delayed(p_do)(idx, signal, order, a) for idx in xrange(order, N))
    

    #plt.plot(pred, 'r')
    #plt.plot(np.abs(sig.lfilter([1, 0, -16, 0,  16, 0, -1], [-16], signal)), 'b')
    #plt.show()
    
    return pred
    
    
'''
Created on Aug 1, 2013

@author: Wiehan
'''

from __future__ import division
import numpy as np
cimport numpy as np
import windowing
import fftw_wrapper.fftw_py as mfftw

def periodogram(signal, window=windowing.apply_blackman_harris, interpolation_factor=1, inplace_windowing=False, disable_normalize=False):
    '''
    Performs the periodogram spectral estimation technique on
    the data.
    
    signal - the vector being analysed
    window - any function that accepts a vector and adheres to
             the interface specified in the windowing module
    interpolation_factor - specifies the length of the frequency
             vector: len(signal)*interpolation_factor
             
    Returns a frequency vector.
    '''
    
    N = len(signal)

    if window is not None:
        signal = window(signal, inplace=inplace_windowing)

    fft_ = mfftw.real_fft(signal, interpolation_factor * N)
    fft_ = np.abs(np.square(fft_))
    
    if disable_normalize:
        return fft_
    return fft_ / N

def bartlett(signal, K, window=windowing.apply_blackman, interpolation_factor=1):
    '''
    Performs the bartlett spectral estimation technique on
    the data. It calculates K, non-overlapping periodograms
    and averages them together. This results in better variance
    but decreased spectral resolution.
    
    If the length of the signal is not a multiple of K, the last
    N % K samples are discarded, rather than introducing wider than
    normal lobes into the estimate.
    
    signal - the vector being analysed
    K      - the number of segments the data is to be divided into
    window - any function that accepts a vector and adheres to
             the interface specified in the windowing module
    interpolation_factor - specifies the length of the frequency
             vector: len(signal)*interpolation_factor
             
    Returns a frequency vector.
    '''
    cdef int segment_width = int(len(signal) / K)
    cdef np.ndarray[dtype = np.float64_t] output_buffer = np.zeros((segment_width * interpolation_factor / 2 + 1,), dtype=np.float64)
    cdef int idx = 0
    
    for idx in xrange(0, len(signal), segment_width):
        if len(signal) - idx < segment_width:
            break
        output_buffer += periodogram(signal[idx:idx + segment_width], window, interpolation_factor=interpolation_factor)
        
    return output_buffer / K

def welch(signal, W, window=windowing.apply_blackman, interpolation_factor=1):
    '''
    Performs the welch spectral estimation technique on
    the data. It calculates len(signal)-W, overlapping periodograms
    and averages them together. This results in better variance
    but decreased spectral resolution.
    
    signal - the vector being analysed
    W      - width of sliding window
    window - any function that accepts a vector and adheres to
             the interface specified in the windowing module
    interpolation_factor - specifies the length of the frequency
             vector: len(signal)*interpolation_factor
             
    Returns a frequency vector.
    
    TODO: This can be optimised:
        1) More parallelism exploited
        2) Avoid unnecessary buffer allocations
        3) Avoid recomputing the window function every time
    '''

    cdef np.ndarray[dtype = np.float64_t] output_buffer = np.zeros((W * interpolation_factor / 2 + 1,), dtype=np.float64)
    cdef int idx = 0
    
    skip = int((1.0 - windowing.overlap[window])*W)
    count = 0
    
    for idx in xrange(0, len(signal)-W, skip):
        output_buffer += periodogram(signal[idx:idx + W], window, interpolation_factor=interpolation_factor)
        count += 1
        
    return output_buffer / count
#     

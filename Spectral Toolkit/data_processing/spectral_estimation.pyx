'''
Created on Aug 1, 2013

@author: Wiehan
'''

from __future__ import division
import numpy as np
cimport numpy as np
import windowing
import fftw_wrapper.fftw_py as mfftw

def periodogram(signal, window=windowing.apply_blackman, interpolation_factor=1, inplace_windowing=False):
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
    fft_ = np.abs(fft_)
    fft_ = np.square(fft_)
    
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
    
    for idx in xrange(0, len(signal)-W, 1):
        output_buffer += periodogram(signal[idx:idx + W], window, interpolation_factor=interpolation_factor)
        
    return output_buffer / idx


# if __name__ == '__main__':
#     import matplotlib.pyplot as plt
#     import matplotlib.cm as cm
#     
#     fs = 1000
#     f0 = 10.3
#     f1 = 490.9
#     N = 10000
#     t = np.arange(0, N / fs, 1 / fs)
#     sig1 = np.sin(2 * np.pi * f0 * t)
#     sig2 = np.sin(2 * np.pi * f1 * t)
#     signal = np.hstack((sig1, sig2))
#     print len(signal)
#     plt.plot(signal)
#     plt.show()
#     
#     R, Z = stft(signal, 500, zp_fact=1)
#     Z = np.transpose(Z)
#     fig, ax = plt.subplots()
# 
#     im = plt.pcolormesh(Z, vmin=abs(Z).min(), vmax=abs(Z).max())
#     # im.set_interpolation('bilinear')
#     
#     cb = fig.colorbar(im, ax=ax)
#     plt.show()
#     

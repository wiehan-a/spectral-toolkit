'''
Created on Sep 24, 2013

@author: Wiehan
'''
from __future__ import division

import filter_design
import convolution

import numpy as np
cimport numpy as np

transition_band = 0.01
attenuation = 60

def decimate(signal, factor, sampling_rate):
    '''
    Decimate the signal by the integer factor provided.
    
    Destroys the original signal.
     
    Filtering is performed mitigate aliasing.
    
    A new vector is returned.
    '''
    
    assert type(factor) == int
    
    cut_off_frequency = sampling_rate / factor
    filter = filter_design.design_low_pass_fir(cut_off_frequency, transition_band * cut_off_frequency, attenuation, sampling_rate)
    
    if len(filter) >= len(signal):
        print 'Filter length exceeds signal length'
    
    signal = convolution.fast_convolve_fftw_w(signal, filter)
    
    decimated = np.empty(shape=(ceil(len(signal) / factor),), dtype=np.float64)
    decimated[:] = signal[0:factor:]
    
    return decimated
        
    
    

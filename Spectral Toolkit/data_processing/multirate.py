'''
Created on Sep 24, 2013

@author: Wiehan
'''
from __future__ import division

import filter_design
import convolution

import numpy as np

transition_band = 0.1
attenuation = 60

def decimate(signal, factor):
    '''
    Decimate the signal by the integer factor provided.
    
    Destroys the original signal.
     
    Filtering is performed mitigate aliasing.
    
    A new vector is returned.
    '''
    
    assert type(factor) == int
    
    cut_off_frequency = 1 / factor
    filter = filter_design.design_low_pass_fir(cut_off_frequency, transition_band * cut_off_frequency, attenuation, 1)
    
    delay = (len(filter)-1)/2
    
    if len(filter) >= len(signal):
        print 'Filter length exceeds signal length'
    
    #signal = np.convolve(signal, filter)
    signal = convolution.fast_convolve_fftw_w(signal, filter)
    
    decimated = np.empty(shape=(np.ceil(len(signal[delay+1:]) / factor),), dtype=np.float64)
    decimated[:] = signal[delay+1::factor]
    
    return decimated
        
    
    

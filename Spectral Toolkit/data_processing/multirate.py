'''
Created on Sep 24, 2013

@author: Wiehan
'''
from __future__ import division

import filter_design
import convolution

import numpy as np

import matplotlib.pyplot as plt

transition_band = 0.07
attenuation = 120

class NotEnoughSamplesException(Exception):
    pass

def decimate(signal, factor, previous_samples=None):
    '''
    Decimate the signal by the integer factor provided.
    
    Destroys the original signal.
     
    Filtering is performed to mitigate aliasing.
    
    A new vector is returned.
    '''
    
    assert type(factor) == int
    
    cut_off_frequency = 0.5 / factor
    filter = filter_design.design_low_pass_fir(cut_off_frequency, transition_band * cut_off_frequency, attenuation, 1)
    
    print len(signal), len(filter), factor
#     print len(signal), len(filter)
    
    delay = int((len(filter) - 1) / 2)
    
    if len(filter) >= len(signal):
        raise NotEnoughSamplesException('Filter length exceeds signal length, try relaxing constraints')
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
    
    # signal = np.convolve(signal, filter)
    signal = convolution.fast_convolve_fftw_w(signal, filter, delay=delay)
#     print len(signal)
    
    decimated = np.zeros(shape=(np.ceil(len(signal) / factor),), dtype=np.float64)
    print len(decimated), len(signal[::factor])
    decimated[:] = np.ascontiguousarray(np.copy(signal[::factor]))
    
    return decimated
        
    
    

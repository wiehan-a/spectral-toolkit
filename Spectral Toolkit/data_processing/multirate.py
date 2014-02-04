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

max_chunk_size = 5800000

class NotEnoughSamplesException(Exception):
    pass

def decimate(signal, factor, previous_samples=None, transition_band=transition_band, attenuation=attenuation):
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
        #raise NotEnoughSamplesException('Filter length exceeds signal length, try relaxing constraints')
        return signal
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
    decimated = np.zeros(shape=(0,), dtype=np.float64)
    
    offset = 0
    dec_offset = 0
    
    prev_block = None
    while offset < len(signal):
        chunk = np.ascontiguousarray(signal[offset : offset + max_chunk_size])
        
        filtered = convolution.fast_convolve_fftw_w(chunk, filter, delay=delay, prev_block=prev_block)
        
        offset += max_chunk_size
        prev_block = chunk[1 - len(filter):]
        decimated = np.ascontiguousarray(np.hstack((decimated, filtered[dec_offset::factor])))
        dec_offset = (dec_offset + 1) % factor
    
    
    
    return decimated
        
    
    

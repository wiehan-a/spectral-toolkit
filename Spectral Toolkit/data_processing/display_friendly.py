'''
Created on Oct 1, 2013

@author: Wiehan
'''

from __future__ import division

import multirate
import matplotlib.pyplot as plt


TARGET_LENGTH = 20000

def rescale_annotations(annotations, factor):
    if annotations is not None:
        for interval in annotations:
            interval[0] /= factor
            interval[1] /= factor
    

def downsample_for_display(signal, target_length=TARGET_LENGTH, buffered=False, annotations=None):
    '''
    Downsamples the signal until it is of an appropriate length
    to be displayed onscreen.
    '''
    
    while len(signal) >= 2 * target_length:
        decimation_factor = int(len(signal) / target_length)
         
        if decimation_factor > 10:
            signal = multirate.decimate(signal, 10, transition_band=0.12, attenuation=60)
            rescale_annotations(annotations, 10)
        else:
            return signal, annotations
            
            # signal = multirate.decimate(signal, decimation_factor)
    
    print "disp len", len(signal)
    return signal, annotations
            
        

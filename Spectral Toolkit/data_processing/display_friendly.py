'''
Created on Oct 1, 2013

@author: Wiehan
'''
import multirate
import matplotlib.pyplot as plt

TARGET_LENGTH = 20000

def downsample_for_display(signal, target_length=TARGET_LENGTH, buffered=False):
    '''
    Downsamples the signal until it is of an appropriate length
    to be displayed onscreen.
    '''
    while len(signal) >= 2 * target_length:
        decimation_factor = int(len(signal) / target_length)
         
        if decimation_factor > 10:
            signal = multirate.decimate(signal, 10)
        else:
            return signal
            # signal = multirate.decimate(signal, decimation_factor)
             
    return signal
            
        

'''
Created on Oct 1, 2013

@author: Wiehan
'''
import multirate

TARGET_LENGTH = 5000

def downsample_for_display(signal, target_length=TARGET_LENGTH):
    '''
    Downsamples the signal until it is of an appropriate length
    to be displayed onscreen.
    '''
    
    while len(signal) >= 2*target_length:
        decimation_factor = int(len(signal) / target_length)
        
        if decimation_factor > 10:
            signal = multirate.decimate(signal, 10)
        else:
            signal = multirate.decimate(signal, decimation_factor)
            
    return signal
            
        
'''
Created on Oct 2, 2013

@author: Wiehan
'''

import numpy as np
cimport numpy as np
from cython.parallel import prange
import cython
from data_processing.display_friendly import *, downsample_for_display

import matplotlib.pyplot as plt

@cython.boundscheck(False)
def find_discontinuities(np.ndarray[np.float64_t] signal, double tolerance=4, max_back=10):
    '''
    
    '''
    
    cdef float std = 0
    cdef int idx = 0
    cdef int state = 0
    cdef int start_pos = 0
    cdef int x = len(signal)
    cdef float difference
    
    with nogil:
        for idx in prange(1, x, num_threads=8):
            difference = signal[idx] - signal[idx - 1]
            std += difference * difference
    
    std = np.sqrt(std / x)
    
    events = []
    
    cdef float threshold = tolerance * std
    
    for idx in xrange(1, len(signal)):
        difference = signal[idx] - signal[idx - 1]
        
        if difference < 0:
            difference *= -1
            
        if state == 0:
            if difference > threshold:
                state = 1
                start_pos = idx
        elif state == 1:
            if difference > threshold:
                state = 2
            else:
                state = 0
        elif state == 2:
            if difference < threshold:
                events.append((start_pos, idx - 1))
                state = 0
         
    last_event_end = 0
    for idx, tup in enumerate(events):
        back = max(0, last_event_end + 1, tup[0] - max_back)
        view = signal[back:tup[0]+1]
        if len(view) == 0:
            print 'empty slice', back, tup[0]
        baseline = np.mean(view)
        window = np.exp(np.log(0.0001) / len(view) * np.arange(len(view)))
        signal[back : tup[0] + 1] = (signal[back : tup[0] + 1] - baseline) * window + baseline

        signal[tup[0]: tup[1] + 1] = baseline
        
        next_event_start = 0
        if idx == len(events) - 1:
            next_event_start = len(signal)
        else:
            next_event_start = events[idx + 1][0]
        
        forward = min(len(signal), next_event_start + 1, tup[1] + max_back)
        end_baseline = np.mean(signal[tup[1] + 1:forward])
        
        view = signal[tup[1] + 1:forward]
        window = np.exp(np.log(0.0001) / len(view) * np.arange(len(view)))[::-1]
        signal[tup[1] + 1:forward] = (signal[tup[1] + 1:forward] - end_baseline) * window + end_baseline
        
        jump = -(end_baseline - baseline)
        signal[tup[1] + 1:next_event_start] = signal[tup[1] + 1:next_event_start] + jump
        
        last_event_end = tup[1]
            
    
    return signal, events
    
    

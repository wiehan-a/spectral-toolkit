'''
Created on Oct 7, 2013

@author: Wiehan
'''

from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
from convolution import *
from multirate import *
from data_processing.convolution import fast_convolve_fftw_w

from data_access.segy import *
from data_processing import multirate, display_friendly

from collections import deque

import bisect, copy

cimport numpy as np
cimport cython

class RidgeLine:
    def __init__(self, start_idx, start_scale):
        self.gap_number = 0
        self.nodes = deque([(start_idx, start_scale)])

def mexican_hat_wavelet(a=1, sampling_rate=1):
    x = np.arange(-a * 5, a * 5 + 1, 1.0 / sampling_rate, dtype=np.float64)
    
    norm = 2 / (np.sqrt(3 * a) * (np.pi ** 0.25))
    xws = -1 * np.square(x / a)
    
    return x, norm * (1 + xws) * np.exp(xws / 2)

def morlet_wavelet(a=1, w=5, sampling_rate=1):
    x = np.arange(-a * 4 * sampling_rate, a * 4 * sampling_rate + 1, 1)
    xa = x / a
    norm = (a ** (-0.5)) * (np.pi ** (-0.25)) * ((1 + np.exp(-1 * w ** 2) - 2 * np.exp(-0.75 * w ** 2)) ** (-0.5))
    
    return x, norm * np.exp(-0.5 * np.square(xa)) * (np.cos(w * xa) - np.exp(-0.5 * np.square(w)))

def cwt(signal, scales, sampling_rate=1):
    print "cwt"
    CWT = None
    for idx, scale in enumerate(scales):
        wavelet = mexican_hat_wavelet(a=scale, sampling_rate=sampling_rate)[1]
        delay = int((len(wavelet) - 1) / 2) + 1
        CWT_ = fast_convolve_fftw_w(signal, wavelet, delay=delay)
#         print delay, len(CWT_)
#         if CWT is None:
#             CWT = CWT_
#         else:
#             CWT = np.vstack((CWT, CWT_))
    
        if CWT is None:
            CWT = np.empty(shape=(len(scales), len(CWT_)), dtype=np.float64)
            
        CWT[idx, :] = CWT_
    return CWT

@cython.boundscheck(False)
def local_maxima(np.ndarray[dtype = np.float64_t] signal, int window):
    maxima = set([])
    cdef int maximum = 0
    cdef int idx
    cdef np.ndarray[dtype = np.float64_t] view
    for idx in xrange(0, len(signal), 1):
        
        view = signal[idx: idx + window]
        
        if (maximum != idx - 1) and view[-1] < signal[maximum]:
            continue
        
        maximum = idx + np.argmax(view)
        
        left = True
        right = True
        
        if maximum != 0:
            left = signal[maximum] > signal[maximum - 1]
        if maximum != len(signal) - 1:
            right = signal[maximum] > signal[maximum + 1]
        
        if left and right:
            maxima.add(maximum)
    
    return sorted(list(maxima))

def find_ridges(ridge_list, scales, gap_threshold=3, distance_scale=1.05):
    print "ridgelines"
    ridge_list = copy.deepcopy(ridge_list)
    ridge_lines = [RidgeLine(x, len(scales) - 1) for x in ridge_list[-1]]
    idx = len(ridge_list) - 2
    
    removed = set([])
    
    while idx >= 0:
        rs = ridge_list[idx]
        new_list = deque([])
        for idx2, ridge_line in enumerate(ridge_lines):
            last_node = ridge_line.nodes[-1][0]
            
            try:
                bisect_ = bisect.bisect_left(rs, last_node)
                right = rs[bisect_]
                left = rs[bisect_ - 1]
            except IndexError:
                print 'Last node left dangling'
                break
            
            right_dist = np.abs(last_node - right)
            left_dist = np.abs(last_node - left)
            closest_dist_arg = np.argmin([left_dist, right_dist])
            closest_dist = [left_dist, right_dist][closest_dist_arg]
            closest = [bisect_ - 1, bisect_][closest_dist_arg]
            rejected = closest_dist > scales[idx] * distance_scale
            
            if not rejected:
                ridge_line.gap_number = 0
                ridge_line.nodes.append((rs[closest], idx))
                removed.add(rs[closest])
            else:
                ridge_line.gap_number += 1
                
            if ridge_line.gap_number < gap_threshold:
                new_list.append(ridge_line)

        if idx > gap_threshold:
            for x in list(set(rs) - removed):
                new_list.append(RidgeLine(x, idx))
        
        ridge_lines = new_list
            
        idx -= 1
    
    return ridge_lines

def max_coefficient_along_ridge(ridge_line, cwt_matrix):
    max = float('-inf')
    for a, b in ridge_line.nodes:
        t = cwt_matrix[b, a]
        if t > max:
            max = t
    return max

def percentile(data, percent=0.95):
    '''
    Adapted from: http://code.activestate.com/recipes/511478
    '''
    data = sorted(data)
    k = percent * (len(data) - 1)
    f = int(np.floor(k))
    c = int(np.ceil(k))
    if f == c:
        return data[f]
    d0 = data[f] * (c - k)
    d1 = data[c] * (k - f)
    return d0 + d1

def ridge_snrs(ridge_lines, cwt_matrix, window_fact=0.1):
    window_half_length = int(window_fact * len(cwt_matrix[0]) / 2.0)
    x = np.empty(shape=(len(ridge_lines)), dtype=np.float64)
    snr = np.empty(shape=(len(ridge_lines)), dtype=np.float64)
    for idx, ridge_line in enumerate(ridge_lines):
        signal_strength = max_coefficient_along_ridge(ridge_line, cwt_matrix)
        windowed = np.abs(cwt_matrix[0, max(0, ridge_line.nodes[-1][0] - window_half_length) : min(ridge_line.nodes[-1][0] + window_half_length, len(cwt_matrix[0]))])
        noise_score = max(percentile(windowed, percent=0.95), 0.01)
        x[idx] = np.median(ridge_line.nodes)
        snr[idx] = signal_strength / noise_score
    
    return x, snr

def peak_detection(arrx, sampling_rate):
    arrx, _ = display_friendly.downsample_for_display(arrx, target_length=20000)
    f_scale = sampling_rate * np.arange(len(arrx)) / 2 / len(arrx)
    
    ridge_list = []
    scales = np.arange(2, 100, 2)
    CWT = cwt(arrx, scales, sampling_rate=1)
    print "maxima"
    for scale in xrange(1, len(CWT) + 1):
        maxima = local_maxima(CWT[scale - 1, :], 5 * scale)
        ridge_list.append(maxima)
    ridge_lines = find_ridges(ridge_list, scales)
    x_snr, snr = ridge_snrs(ridge_lines, CWT)
    x_snr = (sampling_rate) * x_snr / len(arrx)
    
    return arrx, x_snr, snr    
    
    

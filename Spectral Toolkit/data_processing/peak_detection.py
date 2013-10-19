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

import bisect, copy

class RidgeLine:
    def __init__(self, start_idx, start_scale):
        self.gap_number = 0
        self.start_scale = start_scale
        self.nodes = [start_idx]

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
    CWT = None
    for scale in scales:
        wavelet = mexican_hat_wavelet(a=scale, sampling_rate=sampling_rate)[1]
        delay = int((len(wavelet) - 1) / 2) + 1
        CWT_ = fast_convolve_fftw_w(signal, wavelet, delay=delay)
#         print delay, len(CWT_)
        if CWT is None:
            CWT = CWT_
        else:
            CWT = np.vstack((CWT, CWT_))
    
    return CWT

def local_maxima(signal, window):
    maxima = set([])
    for idx in xrange(0, len(signal), 1):
        view = signal[idx: idx + window]
        maximum = idx + np.argmax(view)
        
        left = True
        right = True
        
        if maximum != 0:
            left = signal[maximum] > signal[maximum - 1]
        if maximum != len(signal) - 1:
            right = signal[maximum] > signal[maximum + 1]
        
        if (maximum not in maxima) and left and right:
            maxima.add(maximum)
    
    return sorted(list(maxima))

def find_ridges(ridge_list, scales, gap_threshold=3, distance_scale=1.05):
    ridge_list = copy.deepcopy(ridge_list)
    ridge_lines = [RidgeLine(x, len(scales) - 1) for x in ridge_list[-1]]
    idx = len(ridge_list) - 2
    
    while idx >= 0:
        rs = ridge_list[idx]
        new_list = []
        for idx2, ridge_line in enumerate(ridge_lines):
            last_node = ridge_line.nodes[-1]
            
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
                ridge_line.nodes.append(rs[closest])
                del rs[closest]
            else:
                ridge_line.gap_number += 1
                
            if ridge_line.gap_number < gap_threshold:
                new_list.append(ridge_line)

        if idx > gap_threshold:
            for x in rs:
                new_list.append(RidgeLine(x, idx))
        
        ridge_lines = new_list
            
        idx -= 1
    
    return ridge_lines

def max_coefficient_along_ridge(ridge_line, cwt_matrix):
    max = float('-inf')
    for a, b in zip(range(ridge_line.start_scale, ridge_line.start_scale - len(ridge_line.nodes), -1), ridge_line.nodes):
        t = cwt_matrix[a, b]
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
        windowed = np.abs(cwt_matrix[0, max(0, ridge_line.nodes[-1] - window_half_length) : min(ridge_line.nodes[-1] + window_half_length, len(cwt_matrix[0]))])
        noise_score = percentile(windowed, percent=0.95)
        x[idx] = np.median(ridge_line.nodes)
        snr[idx] = signal_strength / noise_score
    
    return x, snr

def peak_detection(arrx):
    arrx = display_friendly.downsample_for_display(arrx, target_length=20000)
    
    ridge_list = []
    scales = np.arange(2, 100, 2)
    CWT = cwt(arrx, scales, sampling_rate=1)
    for scale in xrange(1, len(CWT) + 1):
        maxima = local_maxima(CWT[scale - 1, :], 5 * scale)
        ridge_list.append(maxima)
    ridge_lines = find_ridges(ridge_list, scales)
    x_snr, snr = ridge_snrs(ridge_lines, CWT)

    # maxima = local_maxima(arrx, 100)
    
    fig = plt.figure()
    ax = fig.add_subplot(211)
    ax.plot(arrx)
    
    for x, s in zip(x_snr, snr):
        if s >= 15:
            ax.plot(x, arrx[x], 'ro')
        elif s >= 10:
            ax.plot(x, arrx[x], 'yo')
        elif s >= 5:
            ax.plot(x, arrx[x], 'bo')
        
    print len(arrx)
    
#     for m in maxima:
#         plt.plot(m, arrx[m], 'rx')


#     ax = fig.add_subplot(312)
#     
#     imgplot = ax.imshow(CWT)
#     imgplot.set_cmap('spectral')
#     ax.set_aspect(70)
#     plt.colorbar(mappable=imgplot)
    

#         for m in maxima:
#             plt.plot(m, scale, 'bx')

#     for rl in ridge_lines:
#         for x in rl.nodes:
#             scale_list = list(reversed(np.arange(rl.start_scale - len(rl.nodes) + 1, rl.start_scale + 1)))        
#             plt.plot(rl.nodes, scale_list, 'b-')
            
    ax = fig.add_subplot(212)
    ax.stem(x_snr, snr)
    plt.show()
    
    

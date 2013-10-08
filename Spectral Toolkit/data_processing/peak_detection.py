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
from data_processing import multirate

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
#         plt.plot(wavelet)
#         plt.show()
#         print len(wavelet)
        delay = int((len(wavelet) - 1) / 2)
        
        CWT_ = np.convolve(np.hstack((signal, np.zeros(delay + 1, dtype=np.float64)))  , wavelet)[delay + 1:-len(wavelet)]
#         print len(CWT_)
#         CWT_ = multirate.decimate(CWT_, 10)
#         CWT_ = multirate.decimate(CWT_, 10)
#         CWT_ = multirate.decimate(CWT_, 10)
        
        if CWT is None:
            CWT = CWT_
        else:
            # CWT = np.vstack((CWT, 20 * np.log10(np.abs((CWT_)))))
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

def find_ridges(ridge_list, scales, gap_threshold=3, distance_scale=1.1):
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
    
        
    
if '__main__' == '__main__':
#     ws = [1, 4, 8, 16]
#     for w in ws:
#         x, y = morlet_wavelet(a=w, sampling_rate=1)
#         plt.plot(x, y, 'x-')
#     plt.show()
    arrx = np.load('last.spec')
#     arrx = multirate.decimate(arrx, 10)
#     arrx = multirate.decimate(arrx, 10)
#     arrx = multirate.decimate(arrx, 10)

    # maxima = local_maxima(arrx, 100)
    fig = plt.figure()
    ax = fig.add_subplot(211)
    ax.plot(arrx)
    print len(arrx)
    
#     for m in maxima:
#         plt.plot(m, arrx[m], 'rx')


    scales = np.arange(2, 100, 2)
    ax = fig.add_subplot(212)
    CWT = cwt(arrx, scales, sampling_rate=1)
    imgplot = ax.imshow(CWT)
    imgplot.set_cmap('spectral')
    ax.set_aspect(70)
    plt.colorbar(mappable=imgplot)
    
    ridge_list = []
    
    for scale in xrange(1, len(CWT) + 1):
        maxima = local_maxima(CWT[scale - 1, :], 5 * scale)
        ridge_list.append(maxima)
#         for m in maxima:
#             plt.plot(m, scale, 'bx')

    for rl in find_ridges(ridge_list, scales):
        for x in rl.nodes:
            scale_list = list(reversed(np.arange(rl.start_scale - len(rl.nodes) + 1,  rl.start_scale+1)))        
            plt.plot(rl.nodes, scale_list, 'b-')
            
    plt.show()
    
    

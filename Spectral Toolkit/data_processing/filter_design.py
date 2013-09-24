'''
Created on Sep 24, 2013

@author: Wiehan
'''

from __future__ import division
import numpy as np
import warnings
import matplotlib.pyplot as plt
import numpy.fft as fft

def bessel_first_kind_order_zero(x, tolerance=1e-9, max_iters=100):
    '''
        Calculates the modified Bessel function of the first
        kind at x.
        
        Uses the series expansion given by:
        http://mathworld.wolfram.com/images/equations/ModifiedBesselFunctionoftheFirstKind/NumberedEquation7.gif
    '''
    v = 0.25 * x ** 2
    k = 1
    accumulator = 1
    delta = 1
    while np.abs(delta) > tolerance:
        delta = delta * v / (k ** 2)
        accumulator += delta
        k += 1
        if k > max_iters:
            print 'Max iters reached'
            break
    return accumulator
    
    

def design_low_pass_fir(fc, delta_f, att, sampling_rate):
    '''
        Designs a low pass FIR filter, using the Kaiser
        window method.
        
        fc - cut-off frequency
        delta_f - width of transition band
        att - minimum stopband attenuation of filter (dB)
        
    '''
    
    delta_w = 2 * np.pi * delta_f / sampling_rate
    
    beta = 0
    if att > 21:
        if att > 50:
            beta = 0.1102 * (att - 8.7)
        else:
            beta = 0.5842 * (att - 21.0) ** (0.4) + 0.07886 * (att - 21)
    
    M = (att - 8) / (2.285 * delta_w)
    alpha = M / 2
    
    n = np.arange(0, M, 1)
    n_centered = n - alpha
    wn = beta * np.sqrt((1 - np.square(n_centered / alpha)))
    bessel_vectorized = np.vectorize(bessel_first_kind_order_zero)
    wn = bessel_vectorized(wn)
    ideal_filter = 2 * fc / sampling_rate * np.sinc(2 * fc / sampling_rate * n_centered)
    
    return wn * ideal_filter
    
if __name__ == '__main__':
    filter = design_low_pass_fir(60, 1, 120, 125)
    print filter
    print len(filter)
    plt.plot(filter, '*-')
    plt.show()
    
    plt.plot(20 * np.log10(np.abs(fft.fft(filter, 5 * len(filter)))))
    plt.show()

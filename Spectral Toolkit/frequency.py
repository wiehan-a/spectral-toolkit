'''
Created on Aug 1, 2013

@author: Wiehan
'''

from __future__ import division
from scipy.fftpack import fft
import scipy.signal as sig
import numpy as np

def periodogram(data, window=None, zp_fact=6):
    N = len(data)
    windowed = data
    if window is not None:
        windowed = window(N)*data
    windowed = np.hstack((windowed, np.zeros((zp_fact-1)*N)))
    fft_ = fft(windowed)[0:len(windowed)/2]
    fft_ = np.abs(fft_)
    fft_ = np.square(fft_)
    return fft_/N

def welch(data):
    pass

def stft(data, windowlength, zp_fact=1):
    N = len(data)
    K = windowlength
    
    if N % K != 0:
        raise Exception()
    
    R = N/K
    data = data.reshape(R, K)
    data = np.apply_along_axis(periodogram, 1, data, sig.hanning, zp_fact)
    return R, data    

def bartlett(data, windowlength, zp_fact=1):
    R, data = stft(data, windowlength, zp_fact)
    return np.add.reduce(data)/R

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    
    fs = 1000
    f0 = 10.3
    f1 = 490.9
    N = 10000
    t = np.arange(0,N/fs, 1/fs)
    sig1 = np.sin(2*np.pi*f0*t)
    sig2 = np.sin(2*np.pi*f1*t)
    signal = np.hstack((sig1, sig2))
    print len(signal)
    plt.plot(signal)
    plt.show()
    
    R, Z = stft(signal, 500, zp_fact=1)
    Z = np.transpose(Z)
    fig, ax = plt.subplots()

    im = plt.pcolormesh(Z, vmin=abs(Z).min(), vmax=abs(Z).max())
    #im.set_interpolation('bilinear')
    
    cb = fig.colorbar(im, ax=ax)
    plt.show()
    
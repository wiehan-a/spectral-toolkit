'''
Created on Sep 4, 2013

@author: Wiehan
'''
from __future__ import division
import time, util
import numpy as np
from segy import *
import scipy.signal as sig
from scipy.signal.signaltools import lfilter
import matplotlib.pyplot as plt
import frequency as fr
import sigproc

import cPickle, os

FILES = ["2011.08.04-00.00.00.FR.MGN.00.CGE.SEGY", "2011.08.05-00.00.00.FR.MGN.00.CGE.SEGY",  "2011.08.06-00.00.00.FR.MGN.00.CGE.SEGY"]
DOWNSAMPLE_FACTOR = 10

REMOVE_DISCONTINUITIES = True

DRAW_IN_LOG_DOMAIN = True
START_FREQUENCY = 1e-3
END_FREQUENCY = 125/2/10

DO_NORMALISATION = True
NORMALISATION_ORDER = 1
DRAW_NORMALISATION_CURVE = True

WINDOW = sig.blackman
ZERO_PADDING_FACTOR = 3
FREQUENCY_RESOLUTION_FACTOR = 0.8

'''
    periodogram
    bartlett
    welch
    autogregressive
    
'''
ESTIMATION_MODE = 'bartlett'
DRAW_ESTIMATED_SPECTRUM = True


def downsample(data, factor):

    if os.path.exists("downsample.cache"):
        pkl_file = open('downsample.cache', 'rb')
        ds = cPickle.load(pkl_file)
        pkl_file.close()
    else:
        ds = sig.decimate(data, factor)
        output = open('downsample.cache', 'wb')
        cPickle.dump(ds, output)
        output.close()
        
    return ds

def remove_discontinuities(data, model, threshold):
    '''
        use model as predictor, 
        whenever error is more than threshold * std_dev (RMS), readjust sequence to use the predicted value instead
    '''
    prediction_error = None
    

    if os.path.exists("prediction.cache"):
        pkl_file = open('prediction.cache', 'rb')
        prediction_error = cPickle.load(pkl_file)
    else:
        prediction_error = sigproc.predict_signal(data, order=3)
        output = open('prediction.cache', 'wb')
        cPickle.dump(prediction_error, output)
        output.close()
    
    plt.plot(prediction_error, 'r')
    plt.plot(data, 'g')
    plt.plot(np.abs(sig.lfilter([1, 0, -16, 0,  16, 0, -1], [-16], data)), 'b')
    plt.plot(np.abs(sig.lfilter([1, -1], [-1], data)), 'c')
    plt.legend(['linear predictor', 'signal', 'higher order differencer', 'first order differencer'])
    plt.show()
    rms = np.std(prediction_error)
    print "RMS:", rms
    

if __name__ == '__main__':
    time.clock()

    data = read_in_segy(FILES)
    print "Finished reading after: ", time.clock(), "seconds"
    
    if DOWNSAMPLE_FACTOR > 1:
        data = downsample(data, DOWNSAMPLE_FACTOR)
        print "Finished downsampling after: ", time.clock(), "seconds"
        
    if REMOVE_DISCONTINUITIES:
        remove_discontinuities(data, None, 0)
    
    if DO_NORMALISATION:
        a = sigproc.linear_predictor(data, order=NORMALISATION_ORDER)
        data = lfilter(np.hstack((np.array([1]), a)), [1], data)
        print "Finished frequency normalisation after: ", time.clock(), "seconds"
        if DRAW_NORMALISATION_CURVE:
            w, h = sig.freqz(np.hstack((np.array([1]), a)))
            plt.plot(w, 10*np.log10(1/np.abs(h)),'r')
            plt.show()
    
    p = []
    if ESTIMATION_MODE == 'periodogram':
        p = fr.periodogram(data, window=WINDOW, zp_fact=ZERO_PADDING_FACTOR)
        print "Finished frequency estimation (periodogram) after: ", time.clock(), "seconds"
    if ESTIMATION_MODE == 'bartlett':
        p = fr.bartlett(data, len(data)*FREQUENCY_RESOLUTION_FACTOR, zp_fact=ZERO_PADDING_FACTOR)
        print "Finished frequency estimation (bartlett) after: ", time.clock(), "seconds"
    if ESTIMATION_MODE == 'welch':
        pass
    if ESTIMATION_MODE == 'autoregressive':
        pass
    
    if DRAW_ESTIMATED_SPECTRUM:
        if DRAW_IN_LOG_DOMAIN:
            p = 10*np.log10(p)
            N = len(p)
        ref = 125/2/DOWNSAMPLE_FACTOR
        start = int(N*(START_FREQUENCY)/ref)
        end = int(N*(END_FREQUENCY)/ref)
        t = np.arange(0, 125/2/DOWNSAMPLE_FACTOR, (125/2/DOWNSAMPLE_FACTOR) / (N - 0.5))
        p = p[start:end]
        t = t[start:end]
        plt.plot(t, p)
        plt.show()
    
    
    
    
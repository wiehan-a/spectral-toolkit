'''
Created on Oct 3, 2013

@author: Wiehan
'''

from __future__ import division

from PySide.QtCore import *
from config import db
import data_access
from datetime import timedelta
import numpy as np

import matplotlib.pyplot as plt

import data_processing.multirate as multirate
import data_processing.sigproc as sigproc
import data_processing.convolution as convolution
import data_processing.spectral_estimation as spec_est
from data_processing.discontinuity_tool import find_discontinuities

data_engines = {
                   'SANSA' :  data_access.sansa,
                   'LSBB' : data_access.lsbb
               }

class ProcessingWorker(QObject):
    
    done = Signal(np.ndarray)
    update_message = Signal(str)
    
    def __init__(self, signal, params):
        QObject.__init__(self)
        self.signal = signal
        self.params = params
        
    @Slot()
    def do_processing(self):
        N = len(self.signal)
        
        sigpower = None
        if self.params['fix_power']:
            sigpower = np.sum(np.square(self.signal)) / N
        
        interpol_factor = 1
        if self.params['do_interpol']:
            interpol_factor = self.params['interpol_factor']
        
        estimate = None
        if self.params['method'] == 'Periodogram':
            estimate = spec_est.periodogram(self.signal, interpolation_factor=interpol_factor, window=self.params['window'])
        elif self.params['method'] == 'Bartlett':
            estimate = spec_est.bartlett(self.signal, self.params['parameter'], interpolation_factor=interpol_factor, window=self.params['window'])
        elif self.params['method'] == 'Welch':
            estimate = spec_est.welch(self.signal, self.params['parameter'], interpolation_factor=interpol_factor, window=self.params['window'])
        else:
            model, sigma = sigproc.auto_regression(self.signal, self.params['parameter'])
            print sigma
            estimate = sigma / spec_est.periodogram(model, window=None, interpolation_factor=interpol_factor * len(self.signal) / len(model), disable_normalize=True)
            model = None
        
        if self.params['fix_power']:
            print "fixing power"
            estimate_power = np.sum(estimate) / len(estimate)
            estimate = estimate * (sigpower / estimate_power)
            print sigpower, ', ' , np.sum(estimate) / len(estimate)
        self.done.emit(estimate)
        
class PreProcessingWorker(QObject):
    
    done = Signal(np.ndarray, float)
    update_message = Signal(str)
    
    def __init__(self, params):
        QObject.__init__(self)
        self.params = params
        
    @Slot()
    def do_processing(self):
        files = self.params['files']
        
        sr = db[files[0]]['sampling_rate']
        start_sample = sr * (self.params['start_time'] - db[files[0]]['start_time']).total_seconds()
        end_sample = sr * (self.params['end_time'] - db[files[0]]['end_time']).total_seconds() - 1
        
        signal = data_engines[db[files[0]]['source']].read_in_filenames(files)[start_sample : end_sample]
        
        pass_ = 1
        if self.params['fix_discontinuities']:
            self.update_message.emit('Fixing discontinuities (pass ' + str(pass_) + ")")
            p_events = 0
            while pass_ < 20:
                signal, events = find_discontinuities(signal)
                if events == 0 or events == p_events:
                    break
                p_events = events
                pass_ += 1
        
        signal = signal - np.mean(signal)
        
#         print len(signal)
        
        mf = self.params['max_frequency']
        decimation_factor = int((sr / 2.0) / mf)
        
        sr_cpy = sr
        
        self.update_message.emit('Downsampling...')
        
        try:
            while decimation_factor >= 2:
                print len(signal)
                if decimation_factor > 10:
                    signal = multirate.decimate(signal, 10)
                    decimation_factor /= 10
                    sr_cpy /= 10
                else:
                    signal = multirate.decimate(signal, int(decimation_factor))
                    sr_cpy /= int(decimation_factor)
                    decimation_factor /= int(decimation_factor)
        except multirate.NotEnoughSamplesException:
            pass
        
#         print len(signal)

        if self.params['do_whitening']:
            self.update_message.emit('Calculating normalisation model...')
            model,_ = sigproc.auto_regression(signal, self.params['whitening_order'])
            self.update_message.emit('Applying normalisation filter...')
            if self.params['whitening_order'] < 10:
#                 print len(signal)
#                 print len(model)
                signal = convolution.slow_convolve(signal, model)
            else:
                signal = convolution.fast_convolve_fftw_w(signal, model)
        
        self.update_message.emit('Done')
        self.done.emit(signal, sr_cpy)
        
        

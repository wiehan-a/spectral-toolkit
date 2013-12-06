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

from data_access import data_engines

class ProcessingWorker(QObject):
    
    done = Signal(np.ndarray)
    update_message = Signal(str)
    
    def __init__(self, signals, params):
        QObject.__init__(self)
        self.signals = signals
        self.params = params
        
    @Slot()
    def do_processing(self):
        N = len(self.signals[0])
        
        sigpower = []
        if self.params['fix_power']:
            for signal in self.signals:
                sigpower.append(np.sum(np.square(signal)) / N)
        
        interpol_factor = 1
        if self.params['do_interpol']:
            interpol_factor = self.params['interpol_factor']
        
        estimates = []
        
        for signal in self.signals:
            estimate = None
            if self.params['method'] == 'Periodogram':
                estimate = spec_est.periodogram(signal[0 : len(signal)], interpolation_factor=interpol_factor, window=self.params['window'])
            elif self.params['method'] == 'Bartlett':
                estimate = spec_est.bartlett(signal, self.params['parameter'], interpolation_factor=interpol_factor, window=self.params['window'])
            elif self.params['method'] == 'Welch':
                estimate = spec_est.welch(signal, self.params['parameter'], interpolation_factor=interpol_factor, window=self.params['window'])
            else:
                model, sigma = sigproc.auto_regression(signal[0 : len(signal)], self.params['parameter'])
                print sigma
                estimate = sigma / spec_est.periodogram(model, window=None, interpolation_factor=interpol_factor * len(signal) / len(model), disable_normalize=True)
                model = None
            
            if self.params['fix_power']:
                print "fixing power"
                estimate_power = np.sum(estimate) / len(estimate)
                estimate = estimate * (sigpower / estimate_power)
                print sigpower, ', ' , np.sum(estimate) / len(estimate)
            
            estimates.append(estimate)
                
        self.done.emit(estimates)
        
class PreProcessingWorker(QObject):
    
    done = Signal(object, float, list)
    update_message = Signal(str)
    
    def __init__(self, params):
        QObject.__init__(self)
        self.params = params
        
    @Slot()
    def do_processing(self):
        files = self.params['files']
        first_file = files.values()[0][0]
        last_file = files.values()[0][-1]
        
        sr = db[first_file]['sampling_rate']
        start_sample = sr * (self.params['start_time'] - db[first_file]['start_time']).total_seconds()
        print start_sample
        end_sample = -1*sr * (self.params['end_time'] - db[last_file]['end_time']).total_seconds()
        print end_sample
        
        components = files.keys()
        print components
        signals = []
        
        for comp in components:
            signals.append(data_engines[db[first_file]['source']].read_in_filenames(files[comp], start_sample, end_sample, self.params['transducer_coefficient']))
        
        for idx in xrange(len(signals)):
            pass_ = 1
            if self.params['fix_discontinuities']:
                print "before fixing", len(signals[idx])
                signals[idx] = signals[idx][0 : len(signals[idx])]
                print signals[idx]
                self.update_message.emit('Fixing discontinuities (pass ' + str(pass_) + ")")
                p_events = 0
                while pass_ < 20:
                    signals[idx], events = find_discontinuities(signals[idx])
                    print "after fixing", len(signals[idx])
                    if events == 0 or events == p_events:
                        break
                    p_events = events
                    pass_ += 1
        
        mf = self.params['max_frequency']
        
        self.update_message.emit('Downsampling...')
        
        for idx in xrange(len(signals)):
            
            decimation_factor = int((sr / 2.0) / mf)
            sr_cpy = sr
            
            try:
                while decimation_factor >= 2:
                    print len(signals[idx])
                    if decimation_factor > 10:
                        signals[idx] = multirate.decimate(signals[idx], 10)
                        decimation_factor /= 10
                        sr_cpy /= 10
                    else:
                        signals[idx] = multirate.decimate(signals[idx], int(decimation_factor))
                        sr_cpy /= int(decimation_factor)
                        decimation_factor /= int(decimation_factor)
            except multirate.NotEnoughSamplesException:
                pass
        
#         print len(signal)

        if self.params['do_whitening']:
            
            for idx in xrange(len(signals)):
                self.update_message.emit('Calculating normalisation model...')
                model, _ = sigproc.auto_regression(signals[idx], self.params['whitening_order'])
                self.update_message.emit('Applying normalisation filter...')
                if self.params['whitening_order'] < 10:
    #                 print len(signal)
    #                 print len(model)
                    signals[idx] = convolution.slow_convolve(signals[idx], model)
                else:
                    signals[idx] = convolution.fast_convolve_fftw_w(signals[idx], model)
        
        self.update_message.emit('Done')
        self.done.emit(signals, sr_cpy, components)
        
        

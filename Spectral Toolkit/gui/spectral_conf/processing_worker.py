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

import data_processing.multirate as multirate
import data_processing.sigproc as sigproc
import data_processing.convolution as convolution

data_engines = {
                   'SANSA' :  data_access.sansa,
                   'LSBB' : data_access.lsbb
               }

class ProcessingWorker(QObject):
    
    done = Signal()
    update_message = Signal(str)
    
    def __init__(self, params):
        QObject.__init__(self)
        self.params = params
        
    @Slot()
    def do_processing(self):
        pass
        
        
class PreProcessingWorker(QObject):
    
    done = Signal(np.ndarray)
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
        
        signal = data_engines[db[files[0]]['source']].read_in_filenames(files)[start_sample:end_sample]
        
        mf = self.params['max_frequency']
        decimation_factor = int((sr / 2.0) / mf)
        
        self.update_message.emit('Downsampling...')
        signal = multirate.decimate(signal, decimation_factor)
        
        if self.params['do_whitening']:
            self.update_message.emit('Calculating normalisation model...')
            model = sigproc.auto_regression(signal, self.params['whitening_order'])
            self.update_message.emit('Applying normalisation filter...')
            if self.params['whitening_order'] < 10:
                signal = convolution.slow_convolve(signal, model)
            else:
                signal = convolution.fast_convolve_fftw_w(signal, model)
        
        self.done.emit(signal)
        
        
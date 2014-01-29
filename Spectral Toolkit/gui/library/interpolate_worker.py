'''
Created on Oct 1, 2013

@author: Wiehan
'''

from config import *
import data_access.sansa, data_access.lsbb
from datetime import timedelta

from PySide.QtCore import QObject, Slot, Signal

import numpy as np

import matplotlib.pyplot as plt

from data_access import data_engines
from data_processing.sigproc import auto_regression
from data_processing import sigproc, multirate, spectral_estimation
import os
from data_access.sansa import SansaFileBuffer

class InterpolateWorker(QObject):
    
    done = Signal()
    messaging = Signal(str)
    
    def __init__(self, files, parent):
        QObject.__init__(self)
        self.files = files
        self.parent_ = parent
    
    @Slot()
    def interpolate(self):
        
        signals = []
        
        for file in self.files:

            self.messaging.emit('Loading data...')
            try:    
                signal = data_engines[db[file]['source']].read_in_filenames([file])
            except:
                self.messaging.emit("Error reading file.")
                return
    
            signal, annotations = signal, signal.annotations
            signal = np.float64(signal[0 : len(signal)])
            print "PRE LEN:", len(signal)
            
            print signal, annotations
            def span(interval):
                return interval[1] - interval[0]
                
            
            def longest_run(annotations):
                interval = [0, 0]
                start = 0
                for annotation in annotations:
                    new_interval = [start, annotation[0]]
                    if span(new_interval) > span(interval):
                        start = annotation[1]
                        interval = new_interval
                new_interval = [start, len(signal)]
                if span(new_interval) > span(interval):
                    interval = new_interval
                return interval
            
            longest_run = longest_run(annotations)
            if span(longest_run) < 100:
                print "blah :/"
                return
            else:
                signal_pre = np.copy(signal[longest_run[0]:longest_run[-1]])
                self.messaging.emit("Calculating linear predictor...")
                predictor, scale = auto_regression(signal_pre, 5000)
                print "PRED:", predictor
                self.messaging.emit("Calculating missing samples...")
                sigproc.do_prediction(signal, predictor, annotations)
                print "POST LEN:", len(signal)
                self.messaging.emit("Saving result...")
                os.remove(file)
                np.float32(signal).tofile(file)
                
                sig = multirate.decimate(signal, 5, attenuation=40)
                sig = multirate.decimate(sig, 5, attenuation=40)
                sig = multirate.decimate(sig, 4, attenuation=40)
                os.remove(file+".pre")
                np.float32(sig).tofile(file+".pre")
                
                sig = SansaFileBuffer([file])
                sig = 10*np.log10(spectral_estimation.welch(signal, min(int(len(signal)/3), 5000)))
                os.remove(file+".spec_pre")
                np.float32(sig).tofile(file+".spec_pre")
                
            
        
        self.done.emit()
        

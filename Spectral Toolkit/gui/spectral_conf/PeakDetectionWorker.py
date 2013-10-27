'''
Created on Oct 25, 2013

@author: Wiehan
'''

from __future__ import division
from data_processing.peak_detection import peak_detection

from PySide.QtCore import *
from config import db
import data_access
from datetime import timedelta
import numpy as np

import matplotlib.pyplot as plt


class PeakDetectionWorker(QObject):
    
    done = Signal(np.ndarray, np.ndarray, np.ndarray)
    update_message = Signal(str)
    
    def __init__(self, signal, sampling_rate):
        QObject.__init__(self)
        self.signal = signal
        self.sampling_rate = sampling_rate
        
    @Slot()
    def do_processing(self):
        print dir(np.log10)        
        self.signal = np.log10(self.signal)
        arrx, x_snr, snr = peak_detection(self.signal , self.sampling_rate)
        del self.signal
        self.done.emit(arrx, x_snr, snr)
        

'''
Created on Oct 1, 2013

@author: Wiehan
'''

from config import *
import data_access.sansa, data_access.lsbb
from data_processing import display_friendly
from datetime import timedelta

from PySide.QtCore import QObject, Slot, Signal
from plot_view import Plotter

import numpy as np

import matplotlib.pyplot as plt

from data_access import data_engines

class ProcessTDWorker(QObject):
    
    done = Signal(np.ndarray, np.ndarray)
    messaging = Signal(str)
    
    def __init__(self, files, parent):
        QObject.__init__(self)
        self.files = files
        self.parent_ = parent
    
    @Slot()
    def process_td(self):
        files = self.files
        files = sorted(files, key=lambda f: db[f]['start_time'])
        
        self.messaging.emit('Loading data...')
        signal = data_engines[db[files[0]]['source']].read_in_filenames(files)
        self.messaging.emit('Downsampling data for display...')
        signal = display_friendly.downsample_for_display(signal)
        self.messaging.emit('Plotting...')
        signal = signal[0 : len(signal)]
        
        td = (db[files[-1]]['end_time'] - db[files[0]]['start_time']) / len(signal)
         
        x_axis = [db[files[0]]['start_time'] + idx * td for idx in xrange(len(signal))]
        
        self.done.emit(x_axis, signal)
        

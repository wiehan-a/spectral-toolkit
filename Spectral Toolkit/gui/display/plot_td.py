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
    
    done = Signal(np.ndarray, np.ndarray, list)
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
        try:    
            signal = data_engines[db[files[0]]['source']].read_in_filenames(files)
        except:
            self.messaging.emit("Error reading file.")
            return

            
        self.messaging.emit('Downsampling data for display...')
        signal, annotations = display_friendly.downsample_for_display(signal, annotations=signal.annotations)
        self.messaging.emit('Plotting...')
        signal = signal[0 : len(signal)]
        
#         try:
        td = (db[files[-1]]['end_time'] - db[files[0]]['start_time']) / len(signal)
        for annotation in annotations:
            annotation[0] = db[files[0]]['start_time'] + td * int(annotation[0])
            annotation[1] = db[files[0]]['start_time'] + td * int(annotation[1])
#         except:
#             self.messaging.emit("Error reading file.")
#             return
         
        x_axis = [db[files[0]]['start_time'] + idx * td for idx in xrange(len(signal))]
        
        self.done.emit(x_axis, signal, annotations)
        

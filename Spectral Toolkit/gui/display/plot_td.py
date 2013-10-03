'''
Created on Oct 1, 2013

@author: Wiehan
'''

from config import *
import data_access.sansa, data_access.lsbb
from data_processing import display_friendly
from datetime import timedelta

from PySide.QtCore import QObject, Slot
from plot_view import Plotter

import matplotlib.pyplot as plt

data_engines = {
                   'SANSA' :  data_access.sansa,
                   'LSBB' : data_access.lsbb
               }

class MultipleSourcesException(Exception):
    pass

class MultipleComponentsException(Exception):
    pass

class NotContiguousException(Exception):
    pass

class ShowTDWorker(QObject):
    
    def __init__(self, files):
        QObject.__init__(self)
        self.files = files
    
    @Slot()
    def show_td(self):
        files = self.files
        if len(files) > 1:
            sources = set([db[f]['source'] for f in files])
            
            if len(sources) > 1:
                raise MultipleSourcesException()
            
            components = set([db[f]['component'] for f in files])
            
            if len(components) > 1:
                raise MultipleComponentsException()
            
            files = sorted(files, key=lambda f: db[f]['start_time'])
            
            for idx in xrange(len(files) - 1):
                if db[files[idx + 1]]['start_time'] - db[files[idx]]['end_time'] > timedelta(seconds=1):
                    raise NotContiguousException()
        
        signal = data_engines[db[files[0]]['source']].read_in_filenames(files)
        signal = display_friendly.downsample_for_display(signal)
        
        td = (db[files[-1]]['end_time'] - db[files[0]]['start_time']) / len(signal)
        
        x_axis = [db[files[0]]['start_time'] + idx * td for idx in xrange(len(signal))]
        self.plotter = Plotter(x_axis, signal)

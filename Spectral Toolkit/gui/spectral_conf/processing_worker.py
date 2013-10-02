'''
Created on Oct 3, 2013

@author: Wiehan
'''

from PySide.QtCore import *

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
    
    done = Signal()
    update_message = Signal(str)
    
    def __init__(self, params):
        QObject.__init__(self)
        self.params = params
        
    @Slot()
    def do_processing(self):
        print self.params
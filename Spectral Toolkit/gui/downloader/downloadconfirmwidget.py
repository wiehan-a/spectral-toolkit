'''
Created on Sep 17, 2013

@author: Wiehan
'''

from PySide.QtCore import *
from PySide.QtGui import *
import utils
import data_access.lsbb as lsbb

class DownloadConfirmWidget(QWidget):
    
    title = "<h3>Step 2: Confirm download</h3>"
    
    def __init__(self, parameters):
        QWidget.__init__(self)
        
        self.parameters = parameters
        
        print parameters
        
        self.main_vbox = QVBoxLayout(self)
        self.main_vbox.setAlignment(Qt.AlignTop)
        self.main_vbox.setContentsMargins(0, 0, 0, 0)
        
        if self.parameters['source'] == 'LSBB':
            self.LSBBSetup()
        if self.parameters['source'] == 'SANSA':
            self.SANSASetup()
            
    
    @Slot(dict)
    def lsbb_meta_data_done_slot(self, results):
        print results
    
    def LSBBSetup(self):
        self.loading_box = QVBoxLayout()
        self.main_vbox.addLayout(self.loading_box)
        
        self.movie_label = QLabel('Estimated download size: <b>' + 
                                  utils.sizeof_fmt(lsbb.calculate_size(self.parameters)) + 
                                  '</b>')
        self.loading_box.addWidget(self.movie_label)

        
        self.loading_label = QLabel('Local storage required: <b>' + 
                                  utils.sizeof_fmt(lsbb.calculate_size(self.parameters)) + 
                                  '</b>')
        self.loading_box.addWidget(self.loading_label)
        
    
    def SANSASetup(self):
        pass
    
    def get_actions(self, parent):
        
        back = QPushButton('Back')
        back.clicked.connect(parent.go_back)
        
        download = QPushButton('Download')
        download.clicked.connect(parent.download_confirm_slot)
        
        buttons = {'left' : [back],
                   'right' : [download]}
        
        return buttons
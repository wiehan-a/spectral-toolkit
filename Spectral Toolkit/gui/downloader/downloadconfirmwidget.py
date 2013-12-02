'''
Created on Sep 17, 2013

@author: Wiehan
'''

from PySide.QtCore import *
from PySide.QtGui import *
from gui.icons import *

import utils
import data_access.lsbb as lsbb
import data_access.sansa as sansa

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
            self.parameters['access_engine'] = lsbb
        if self.parameters['source'] == 'SANSA':
            self.parameters['access_engine'] = sansa
            
            
        self.setup()
            
    
    def setup(self):
        
        data_engine = self.parameters['access_engine']
        
        self.loading_box = QVBoxLayout()
        self.main_vbox.addLayout(self.loading_box)
        
        self.movie_label = QLabel('Estimated download size: <b>' + 
                                  utils.sizeof_fmt(data_engine.calculate_size(self.parameters)) + 
                                  '</b>')
        self.loading_box.addWidget(self.movie_label)

        
        self.loading_label = QLabel('Local storage required: <b>' + 
                                  utils.sizeof_fmt(data_engine.calculate_size(self.parameters)) + 
                                  '</b>')
        self.loading_box.addWidget(self.loading_label)

    
    def get_actions(self, parent):
        
        back = QPushButton(app_icons['back'], 'Back')
        back.clicked.connect(parent.go_back)
        
        download = QPushButton(app_icons['download'], 'Download')
        download.clicked.connect(parent.download_confirm_slot)
        
        buttons = {'left' : [back],
                   'right' : [download]}
        
        return buttons
'''
Created on Dec 2, 2013

@author: Wiehan
'''

from PySide.QtCore import *
from PySide.QtGui import *
import sys, time, os, utils

from gui import *
from gui.icons import app_icons
from data_access import local_sansa

class Importer(QWidget):
    
    def __init__(self, parent_):

        QWidget.__init__(self)
        self.setWindowTitle('Spectral Toolkit (Local data import)')
        self.setMinimumWidth(500)
        self.parent_ = parent_
        
        self.setWindowIcon(QIcon('icon.png'))
        if os.name == 'nt':
            # This is needed to display the app icon on the taskbar on Windows 7
            import ctypes
            myappid = 'MyOrganization.MyGui.1.0.0' # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
        self.main_vbox = QVBoxLayout(self)
        self.main_vbox.setAlignment(Qt.AlignTop)
        self.header_title_label = QLabel('<h3>Local data import (SANSA)</h3>')
        self.main_vbox.addWidget(self.header_title_label)
        
        self.files_hbox = QHBoxLayout(self)
        self.files_label = QLabel("Files:")
        self.files_hbox.addWidget(self.files_label)
        self.files_edit = QLineEdit()
        self.files_edit.setReadOnly(True)
        self.files_hbox.addWidget(self.files_edit, 5)
        self.files_choose_button = QPushButton("Choose files")
        self.files_choose_button.clicked.connect(self.choose_files_slot)
        self.files_hbox.addWidget(self.files_choose_button)
        self.main_vbox.addLayout(self.files_hbox)
        
        self.details_hbox = QHBoxLayout(self)
        self.sampling_rate_label = QLabel("Sampling rate (Hz):")
        self.details_hbox.addWidget(self.sampling_rate_label)
        self.sampling_rate_edit = QLineEdit()
        self.sampling_rate_edit.setValidator(QDoubleValidator(0.0, 10000.0,5, self))
        self.details_hbox.addWidget(self.sampling_rate_edit)
        self.tag_label = QLabel("Tag:")
        self.details_hbox.addWidget(self.tag_label)
        self.tag_edit = QLineEdit()
        self.details_hbox.addWidget(self.tag_edit)
        self.main_vbox.addLayout(self.details_hbox)
        
        self.main_vbox.addStretch()
        
        self.action_bar_hbox = QHBoxLayout()
        self.action_bar_hbox.addStretch()
        self.import_button = QPushButton(app_icons['import'], "Import")
        self.import_button.clicked.connect(self.do_import)
        self.action_bar_hbox.addWidget(self.import_button)
        self.main_vbox.addLayout(self.action_bar_hbox)
        
        self.setLayout(self.main_vbox)
        
    @Slot()
    def choose_files_slot(self):
        self.file_names = QFileDialog.getOpenFileNames(self, "Choose files", "", "Files (*.*)")[0]
        file_list = ", ".join([os.path.basename(fn) for fn in self.file_names])
        self.files_edit.setText(file_list)
        
    @Slot()
    def do_import(self):
        self.setVisible(False)
        self.parent_.statusBar().showMessage('Importing files...')
        local_sansa.import_files(self.file_names, self.tag_edit.text(), float(self.sampling_rate_edit.text()))
        self.parent_.statusBar().showMessage('Importing done')
        self.parent_.lib.table_model.refreshModel()
    
    def run(self):
        self.show()
        return self
        

        
 


        
 


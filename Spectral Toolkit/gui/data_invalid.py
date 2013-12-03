'''
Created on Dec 2, 2013

@author: Wiehan
'''

from PySide.QtCore import *
from PySide.QtGui import *
import sys, time, os, utils

from gui import *
from gui.stdateedit import *
from gui.icons import app_icons
from data_access import local_sansa

from config import *

class DataInvalidAdder(QWidget):
    
    widget_stack = []
    finished_importing_signal = Signal()
    
    def __init__(self, parent_):

        QWidget.__init__(self)
        self.setWindowTitle('Spectral Toolkit (Add data invalid event)')
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
        self.header_title_label = QLabel('<h3>Add data invalid event</h3>')
        self.main_vbox.addWidget(self.header_title_label)
        
        self.sources_hbox = QHBoxLayout(self)
        self.sources_label = QLabel("Source:")
        self.sources_hbox.addWidget(self.sources_label)
        self.sources_combo = QComboBox(self)
        self.sources = ['SANSA (Hermanus)', 'LSBB (France)']
        self.sources_map = ['SANSA', 'LSBB']
        self.sources_combo.addItems(self.sources)
        self.sources_hbox.addWidget(self.sources_combo)
        self.main_vbox.addLayout(self.sources_hbox)
        
        self.reason_hbox = QHBoxLayout(self)
        self.reason_label = QLabel("Reason:")
        self.reason_hbox.addWidget(self.reason_label)
        self.reason_edit = QLineEdit()
        self.reason_hbox.addWidget(self.reason_edit)
        self.main_vbox.addLayout(self.reason_hbox)
        
        self.date_hbox = QHBoxLayout(self)
        self.main_vbox.addLayout(self.date_hbox)
        start_date_label = QLabel('Start time:')
        self.date_hbox.addWidget(start_date_label)
        self.start_date_dateedit = STDateTimeEdit()
        self.date_hbox.addWidget(self.start_date_dateedit, 2)
        self.date_hbox.addSpacing(10)
        end_date_label = QLabel('End time:')
        self.date_hbox.addWidget(end_date_label)
        self.end_date_dateedit = STDateTimeEdit()
        self.date_hbox.addWidget(self.end_date_dateedit, 2)
        
        self.main_vbox.addStretch()
        
        self.action_bar_hbox = QHBoxLayout()
        self.action_bar_hbox.addStretch()
        self.add_button = QPushButton(app_icons['add_event'], "Add")
        self.add_button.clicked.connect(self.do_add)
        self.action_bar_hbox.addWidget(self.add_button)
        self.main_vbox.addLayout(self.action_bar_hbox)
        
        self.setLayout(self.main_vbox)
        
        
    @Slot()
    def do_add(self):
         self.setVisible(False)
         
         entry = {
                      "Reason" : self.reason_edit.text(),
                      "Start": self.start_date_dateedit.date().strftime("%Y-%m-%d %H:%M:%S"),
                      "End": self.end_date_dateedit.date().strftime("%Y-%m-%d %H:%M:%S"),
                  }
         
         
         maintenance_logs[self.sources_map[self.sources_combo.currentIndex()]].append(entry)
         save_maintenance_logs()
         
         
#         self.parent_.statusBar().showMessage('Importing files...')
#         local_sansa.import_files(self.file_names, self.tag_edit.text(), float(self.sampling_rate_edit.text()))
#         self.parent_.statusBar().showMessage('Importing done')
#         self.parent_.lib.table_model.refreshModel()
    
    def run(self):
        self.show()
        return self
        

'''
Created on Sep 17, 2013

@author: Wiehan
'''

from PySide.QtCore import *
from PySide.QtGui import *

from gui.icons import *

from gui.stdateedit import *

class DataSelectorWidget(QWidget):
    
    title = '<h3>Step 1: Select data source and period</h3>'
    
    def __init__(self):
        QWidget.__init__(self)
        
        self.data_selector_widgets = {'SANSA (Hermanus)' : DataSelectorWidgetSANSA(),
                                      'LSBB (France)' : DataSelectorWidgetLSBB()}
        
        self.main_vbox = QVBoxLayout(self)
        self.main_vbox.setAlignment(Qt.AlignTop)
        self.main_vbox.setContentsMargins(0, 0, 0, 0)
        
        self.originchooser_hbox = QHBoxLayout(self)
        self.main_vbox.addLayout(self.originchooser_hbox)
        origin_label = QLabel('Choose origin:', self)
        self.originchooser_hbox.addWidget(origin_label)    
        self.sources_combo = QComboBox(self)
        self.sources_combo.currentIndexChanged.connect(self.origin_changed_slot)
        self.sources = ['SANSA (Hermanus)', 'LSBB (France)']
        self.sources_combo.addItems(self.sources)
        self.originchooser_hbox.addWidget(self.sources_combo)
        
        self.setLayout(self.main_vbox)
        
    @Slot(str)
    def origin_changed_slot(self, value):
        if hasattr(self, 'data_selector_widget'):
            self.data_selector_widget.setVisible(False)
            self.main_vbox.removeWidget(self.data_selector_widget)
        
        self.data_selector_widget = self.data_selector_widgets[self.sources[value]]
        self.main_vbox.addWidget(self.data_selector_widget)
        self.data_selector_widget.setVisible(True)
        
    
    def validate_self(self):
        return self.data_selector_widget.validate_self()
    
    def get_actions(self, parent):
        
        action_button = QPushButton(app_icons['next'], 'Next')
        action_button.clicked.connect(parent.data_select_slot)
        
        buttons = {'left' : [],
                   'right' : [action_button]}
        
        return buttons
        
class DataSelectorWidgetSANSA(QWidget):
 
    def __init__(self):
        QWidget.__init__(self)
        
        self.main_vbox = QVBoxLayout(self)
        self.main_vbox.setAlignment(Qt.AlignTop)
        self.main_vbox.setContentsMargins(0, 0, 0, 0)
            
        self.date_hbox = QHBoxLayout(self)
        self.main_vbox.addLayout(self.date_hbox)
        start_date_label = QLabel('Start date:')
        self.date_hbox.addWidget(start_date_label)
        self.start_date_dateedit = STDateTimeEdit()
        self.date_hbox.addWidget(self.start_date_dateedit)
        self.date_hbox.addSpacing(10)
        end_date_label = QLabel('End date:')
        self.date_hbox.addWidget(end_date_label)
        self.end_date_dateedit = STDateTimeEdit()
        self.date_hbox.addWidget(self.end_date_dateedit)
              
        
        self.setLayout(self.main_vbox)
            
    def validate_self(self):
        print "I do validate"
        start_date = self.start_date_dateedit.date()
        end_date = self.end_date_dateedit.date()
        
        if start_date > end_date:
            msgBox = QMessageBox();
            msgBox.setText("Start date must be before end date.");
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_();
            return False
        
        return True
    
    def annotateParams(self, params):
        params['start_date'] = self.start_date_dateedit.date()
        params['end_date'] = self.end_date_dateedit.date()
        params['sampling_rate'] = 125
        
class DataSelectorWidgetFile(QWidget):
    
    def __init__(self):
        QWidget.__init__(self)
        
        self.main_vbox = QVBoxLayout(self)
        self.main_vbox.setAlignment(Qt.AlignTop)
        self.main_vbox.setContentsMargins(0, 0, 0, 0)
        
        self.main_vbox.addWidget(QLabel('Not implemented yet (file)'))
        
        self.setLayout(self.main_vbox)
        
    def validate_self(self):
        return True
    
    def annotateParams(self, params):
        pass
 
class DataSelectorWidgetLSBB(QWidget):
 
    def __init__(self):
        QWidget.__init__(self)
        
        self.main_vbox = QVBoxLayout(self)
        self.main_vbox.setAlignment(Qt.AlignTop)
        self.main_vbox.setContentsMargins(0, 0, 0, 0)
        
        self.sampling_hbox = QHBoxLayout(self)
        self.sampling_label = QLabel("Select base sampling rate:")
        self.sampling_hbox.addWidget(self.sampling_label)
        self.sampling_combo = QComboBox()
        self.sampling_rates = ['125 Hz', '500 Hz']
        self.sampling_combo.addItems(self.sampling_rates)
        self.sampling_combo.currentIndexChanged.connect(self.sampling_rate_change_slot)
        self.sampling_hbox.addWidget(self.sampling_combo)
        self.main_vbox.addLayout(self.sampling_hbox)
        
        self.components_hbox = QHBoxLayout(self)
        self.main_vbox.addLayout(self.components_hbox)
        components_label = QLabel('Components:', self)
        self.components_hbox.addWidget(components_label)
        self.components_checkboxes = {sr : [] for sr in self.sampling_rates}
        self.components_list = {'125 Hz' : ['HGE', 'HGN', 'HGZ'],
                           '500 Hz' : ['CGE', 'CGN', 'CGZ']}
        
        for sampling_rate in self.sampling_rates:
            for component in self.components_list[sampling_rate]:
                tmp_check = QCheckBox(component, self)
                tmp_check.setVisible(False)
                self.components_checkboxes[sampling_rate].append(tmp_check)
        
        for chkbx in self.components_checkboxes[self.sampling_rates[0]]:
            self.components_hbox.addWidget(chkbx)
            chkbx.setVisible(True)
            
        self.date_hbox = QHBoxLayout(self)
        self.main_vbox.addLayout(self.date_hbox)
        start_date_label = QLabel('Start date:')
        self.date_hbox.addWidget(start_date_label)
        self.start_date_dateedit = STDateEdit()
        self.date_hbox.addWidget(self.start_date_dateedit)
        self.date_hbox.addSpacing(10)
        end_date_label = QLabel('End date:')
        self.date_hbox.addWidget(end_date_label)
        self.end_date_dateedit = STDateEdit()
        self.date_hbox.addWidget(self.end_date_dateedit)
        # self.date_hbox.addStretch(1)
        
#         self.cache_checkbox = QCheckBox('Cache downloaded data locally')
#         self.main_vbox.addWidget(self.cache_checkbox)
#         self.download_only_checkbox = QCheckBox('Download only')
#         self.main_vbox.addWidget(self.download_only_checkbox)
              
        
        self.setLayout(self.main_vbox)
        
    @Slot()
    def sampling_rate_change_slot(self):
        for sampling_rate in self.sampling_rates:
            for chkbx in self.components_checkboxes[sampling_rate]:
                chkbx.setVisible(False)
                self.components_hbox.removeWidget(chkbx)
        
        for chkbx in self.components_checkboxes[self.sampling_rates[self.sampling_combo.currentIndex()]]:
            self.components_hbox.addWidget(chkbx)
            chkbx.setVisible(True)
            
    def validate_self(self):
        start_date = self.start_date_dateedit.date()
        end_date = self.end_date_dateedit.date()
        
        if start_date > end_date:
            msgBox = QMessageBox();
            msgBox.setText("Start date must be before end date.");
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_();
            return False
        
        return True
    
    def annotateParams(self, params):
        params['start_date'] = self.start_date_dateedit.date()
        params['end_date'] = self.end_date_dateedit.date()
        params['sampling_rate'] = int(self.sampling_rates[self.sampling_combo.currentIndex()].split(' ')[0])
        params['components'] = [ x.text() 
                                 for x in self.components_checkboxes[
                                         self.sampling_rates[self.sampling_combo.currentIndex()]
                                                                    ] 
                                 if x.isChecked() ]
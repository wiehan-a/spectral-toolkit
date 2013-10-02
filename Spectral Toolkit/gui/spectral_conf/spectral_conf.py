'''
Created on Sep 11, 2013

@author: Wiehan
'''

from __future__ import division

from PySide.QtCore import *
from PySide.QtGui import *
import sys, time, os, utils, config

# from gui import *
# from gui.downloader import *
# from gui.downloader.downloadconfirmwidget import *
# from gui.downloader.dataselectorwidgets import *
from gui.stdateedit import *


class SpectralConf(QWidget):
    
    def __init__(self, files):

        QWidget.__init__(self)
        
        self.files = files
        self.files = sorted(self.files, key=lambda f: config.db[f]['start_time'])
        
        self.setWindowTitle('Spectral Toolkit (Data selection)')
        self.setMinimumWidth(500)
        
        self.main_vbox = QVBoxLayout(self)
        self.main_vbox.setAlignment(Qt.AlignTop)
        self.header_title_label = QLabel()
        self.main_vbox.addWidget(self.header_title_label)        
        
        self.hosted_vbox = QVBoxLayout()
        self.main_vbox.addLayout(self.hosted_vbox)
         
        self.hosted_widget = DomainConfigWidget(self)
        self.header_title_label.setText(self.hosted_widget.title)
        self.hosted_vbox.addWidget(self.hosted_widget)
         
        self.main_vbox.addStretch()
         
        self.action_bar_hbox = QHBoxLayout()
        self.main_vbox.addLayout(self.action_bar_hbox)
        self.cancel_button = QPushButton('Cancel')
        self.action_bar_hbox.addWidget(self.cancel_button)
        self.action_bar_hbox.addStretch()
        self.next_button = QPushButton('Next')
        self.next_button.clicked.connect(self.next_slot_domain)
        self.action_bar_hbox.addWidget(self.next_button)
        
        self.setLayout(self.main_vbox)
        
    @Slot()
    def next_slot_domain(self):
        self.params = {
                    'start_time': self.hosted_widget.start_date_dateedit.date(),
                    'end_time': self.hosted_widget.end_date_dateedit.date(),
                    'max_frequency' : float(self.hosted_widget.max_freq_edit.text()),
                    'do_whitening' : self.hosted_widget.whitening_chkbx.isChecked(),
                    'whitening_order' : int(self.hosted_widget.whitening_order_spinner.value()),
                  }
        
        self.hosted_widget.setVisible(False)
        self.hosted_vbox.removeWidget(self.hosted_widget)
        self.hosted_widget = EstimationConfigWidget(self)
        self.hosted_vbox.addWidget(self.hosted_widget)
        self.hosted_widget.setVisible(True)
        
        self.header_title_label.setText(self.hosted_widget.title)
        self.next_button.clicked.disconnect(self.next_slot_domain)
        self.next_button.clicked.connect(self.next_slot_estim)
        
    @Slot()
    def next_slot_estim(self):
        self.params.update({
                                'method' : self.hosted_widget.estimation_methods[self.hosted_widget.method_combo.currentIndex()],
                                'do_interpol' : self.hosted_widget.interpolate_chkbx.isChecked(),
                                'interpol_factor' : float(self.hosted_widget.parameter_edit.text()),
                                'parameter' : int(self.hosted_widget.parameter_edit.text())
                            })
        
        print self.params
        

class DomainConfigWidget(QWidget):
    
    title = "<h3>Step 1: Configure preprocessing options</h3>"
    
    
    def __init__(self, parent_):
        QWidget.__init__(self)
        
        self.parent_ = parent_
        
        self.main_vbox = QVBoxLayout(self)
        self.main_vbox.setAlignment(Qt.AlignTop)
        self.main_vbox.setContentsMargins(0, 0, 0, 0)
        
        self.date_hbox = QHBoxLayout(self)
        self.main_vbox.addLayout(self.date_hbox)
        start_date_label = QLabel('Start time:')
        self.date_hbox.addWidget(start_date_label)
        self.start_date_dateedit = STDateTimeEdit()
        self.start_date_dateedit.setDateTime(QDateTime(config.db[self.parent_.files[0]]['start_time']))
        self.date_hbox.addWidget(self.start_date_dateedit)
        self.date_hbox.addSpacing(10)
        end_date_label = QLabel('End time:')
        self.date_hbox.addWidget(end_date_label)
        self.end_date_dateedit = STDateTimeEdit()
        self.end_date_dateedit.setDateTime(QDateTime(config.db[self.parent_.files[-1]]['end_time']))
        self.date_hbox.addWidget(self.end_date_dateedit)
        
        
        self.frequency_hbox = QHBoxLayout()
        self.main_vbox.addLayout(self.frequency_hbox)
        self.max_freq_label = QLabel('Maximum frequency of interest:')
        self.frequency_hbox.addWidget(self.max_freq_label)
        self.max_freq_edit = QLineEdit(''+str(config.db[self.parent_.files[0]]['sampling_rate']/2))
        self.frequency_hbox.addWidget(self.max_freq_edit)
        self.frequency_hbox.addStretch()
        
        self.discontinuity_chkbx = QCheckBox('Detect and correct time domain discontinuities')
        self.main_vbox.addWidget(self.discontinuity_chkbx)
        
        
        
        
        self.whitening_hbox = QHBoxLayout()
        self.main_vbox.addLayout(self.whitening_hbox)
        self.whitening_chkbx = QCheckBox('Perform spectral whitening')
        self.whitening_chkbx.stateChanged.connect(self.whitening_slot)
        self.whitening_hbox.addWidget(self.whitening_chkbx)
        self.whitening_hbox.addStretch()
        self.whitening_order_label = QLabel('Number of zeroes:')
        self.whitening_hbox.addWidget(self.whitening_order_label)
        self.whitening_order_spinner = QSpinBox()
        self.whitening_order_spinner.setMinimum(1)
        self.whitening_order_spinner.setValue(1)
        self.whitening_order_spinner.setSingleStep(1)
        self.whitening_order_spinner.setEnabled(False)
        self.whitening_hbox.addWidget(self.whitening_order_spinner)
        
    @Slot()
    def whitening_slot(self):
        self.whitening_order_spinner.setEnabled(self.whitening_chkbx.isChecked())
        
        
class EstimationConfigWidget(QWidget):
    
    title = "<h3>Step 2: Configure estimation parameters</h3>"
    
    estimation_methods = ['Periodogram', 'Bartlett', 'Welch', 'Auto-regressive modeling']
    estimation_methods_params = ['', 'Number of segments', 'Segment length', 'Number of poles']
    
    def __init__(self, parent_):
        QWidget.__init__(self)
        
        self.parent_ = parent_
        
        self.main_hbox = QHBoxLayout(self)
        self.main_hbox.setAlignment(Qt.AlignTop)
        self.main_hbox.setContentsMargins(0, 0, 0, 0)
        
        self.left_vbox = QVBoxLayout()
        self.main_hbox.addLayout(self.left_vbox)
        
        self.method_hbox = QHBoxLayout()
        self.left_vbox.addLayout(self.method_hbox)
        self.method_label = QLabel('Estimation method')
        self.method_hbox.addWidget(self.method_label)
        self.method_combo = QComboBox()
        self.method_combo.currentIndexChanged.connect(self.method_changed_slot)
        self.method_combo.addItems(self.estimation_methods)
        self.method_hbox.addWidget(self.method_combo)
        
        self.window_hbox = QHBoxLayout()
        self.left_vbox.addLayout(self.window_hbox)
        self.window_label = QLabel('Data window')
        self.window_hbox.addWidget(self.window_label)
        self.window_combo = QComboBox()
        self.window_combo.addItems(['Blackman'])
        self.window_hbox.addWidget(self.window_combo)
        
        self.interpolate_hbox = QHBoxLayout()
        self.left_vbox.addLayout(self.interpolate_hbox)
        self.interpolate_chkbx = QCheckBox('Interpolate estimated spectrum')
        self.interpolate_hbox.addWidget(self.interpolate_chkbx)
        self.interpolate_edit = QLineEdit('1.0')
        self.interpolate_hbox.addStretch()
        self.interpolate_hbox.addWidget(self.interpolate_edit)
        
        
        self.parameter_hbox = QHBoxLayout()
        self.left_vbox.addLayout(self.parameter_hbox)
        self.parameter_label = QLabel('Number of segments:')
        self.parameter_hbox.addWidget(self.parameter_label)
        self.parameter_edit = QLineEdit('2')
        self.parameter_edit.setEnabled(False)
        self.parameter_hbox.addStretch()
        self.parameter_hbox.addWidget(self.parameter_edit)
        
        self.left_vbox.addStretch()
        
        
        self.right_vbox = QVBoxLayout()
        self.main_hbox.addLayout(self.right_vbox)
        self.main_hbox.setStretchFactor(self.left_vbox, 2)
        self.info_table = QTableWidget(6, 2)
        self.right_vbox.addWidget(self.info_table)
        
        verthead = self.info_table.verticalHeader()
        verthead.setDefaultSectionSize(verthead.fontMetrics().height()+4)
        verthead.hide()
         
        self.info_table.horizontalHeader().setStretchLastSection(True)
        self.info_table.resizeColumnsToContents()
        self.info_table.horizontalHeader().hide()

        
    @Slot(int)
    def method_changed_slot(self, idx):
        try:
            if self.estimation_methods[idx] == 'Periodogram':
                self.parameter_edit.setEnabled(False)
            else:
                self.parameter_edit.setEnabled(True)
                self.parameter_label.setText(self.estimation_methods_params[idx])
        except AttributeError: pass


if __name__ == '__main__':
    qt_app = QApplication(sys.argv)
    
    app = SpectralConf([])
    app.show()
    qt_app.exec_()
        
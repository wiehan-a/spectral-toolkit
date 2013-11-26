'''
Created on Sep 11, 2013

@author: Wiehan
'''

from __future__ import division

import weakref

from PySide.QtCore import *
from PySide.QtGui import *
import sys, time, os, utils, config, struct
from gui.stdateedit import *
from processing_worker import *
import numpy as np
from data_processing import windowing, peak_detection
from data_access import export_fd

from data_processing.display_friendly import downsample_for_display

from gui.display.plot_view import Plotter

from utils import frequency_fmt
from gui.spectral_conf import PeakDetectionWorker

class SpectralConf(QWidget):
    
    closed = Signal(QObject)
    
    def __init__(self, files, parent_):

        QWidget.__init__(self)
        
        self.parent_ = weakref.ref(parent_)
        self.files = files
        self.files = sorted(self.files, key=lambda f: config.db[f]['start_time'])
        
        self.setWindowTitle('Spectral Toolkit (Spectral estimation)')
        self.setMinimumWidth(500)
        
        self.main_vbox = QVBoxLayout(self)
        self.main_vbox.setAlignment(Qt.AlignTop)
        
        self.progress_bar_vbox = QVBoxLayout()
        self.main_vbox.addLayout(self.progress_bar_vbox)
        
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
        self.cancel_button.clicked.connect(self.cancel_slot)
        self.action_bar_hbox.addWidget(self.cancel_button)
        self.action_bar_hbox.addStretch()
        self.next_button = QPushButton('Next')
        self.next_button.clicked.connect(self.next_slot_domain)
        self.action_bar_hbox.addWidget(self.next_button)
        
        self.setLayout(self.main_vbox)
        
    @Slot()
    def cancel_slot(self):
        print "CANCEL"
        
    @Slot()
    def next_slot_domain(self):
        self.params = {
                        'files': self.files,
                      }
        
        self.params.update(self.hosted_widget.get_params())
        
        self.hosted_widget.setVisible(False)
        self.hosted_vbox.removeWidget(self.hosted_widget)
        self.hosted_widget = EstimationConfigWidget(self)
        self.hosted_vbox.addWidget(self.hosted_widget)
        self.hosted_widget.setVisible(True)
        
        self.header_title_label.setText(self.hosted_widget.title)
        self.next_button.clicked.disconnect(self.next_slot_domain)
        self.next_button.clicked.connect(self.next_slot_estim)
        self.next_button.setEnabled(False)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximum(0)
        self.progress_header_label = QLabel('<h4>Performing preprocessing</h4>')
        self.progress_bar_vbox.addWidget(self.progress_header_label)
        self.progress_label = QLabel('Loading data...')
        self.progress_bar_vbox.addWidget(self.progress_label)
        self.progress_bar_vbox.addWidget(self.progress_bar)
        
        self.preprocessing_worker = PreProcessingWorker(self.params)
        self.preprocessing_worker.update_message.connect(self.progress_label.setText)
        self.preprocessing_worker.done.connect(self.preprocessing_done_slot)
        self.preprocess_thread = QThread()
        self.preprocessing_worker.moveToThread(self.preprocess_thread)
        self.preprocess_thread.started.connect(self.preprocessing_worker.do_processing)
        self.preprocess_thread.start()
        self.preprocessing_worker.done.connect(self.preprocess_thread.quit)
        self.preprocess_thread.finished.connect(self.preprocess_thread.deleteLater)
        
    @Slot()
    def test(self):
        print "TTT"
        
    @Slot(np.ndarray, float)
    def preprocessing_done_slot(self, signal, new_sampling_rate):
        self.next_button.setEnabled(True)
        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(1)
        
        self.signal = signal
        
#         print signal 
        
        self.new_sampling_rate = new_sampling_rate
        self.hosted_widget.update_info_table()
        
    @Slot(np.ndarray)
    def processing_done_slot(self, signal):
        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(1)
        self.signal = None
        self.spectrum = signal
        
        self.export_python_button = QPushButton("Export to Python/NumPy")
        self.export_python_button.clicked.connect(self.export_python_spectrum)
        self.export_matlab_button = QPushButton("Export to MATLAB")
        self.export_matlab_button.clicked.connect(self.export_matlab_spectrum)
        self.main_vbox.addWidget(self.export_python_button)
        self.main_vbox.addWidget(self.export_matlab_button)
        self.view_spectrum_button = QPushButton('View spectrum')
        self.view_spectrum_button.clicked.connect(self.view_spectrum_slot)
        self.main_vbox.addWidget(self.view_spectrum_button)
#         self.export_spectrum_button = QPushButton('Export spectrum')
#         self.main_vbox.addWidget(self.view_spectrum_button)
        self.peak_button = QPushButton('Perform peak detection')
        self.peak_button.clicked.connect(self.peak_detection_slot)
        self.main_vbox.addWidget(self.peak_button)
        
    @Slot()
    def export_matlab_spectrum(self):
        f_qt = QFileDialog.getSaveFileName(self, 'Save', filter='*.m')
        script = export_fd.make_matlab(self.params, self.new_sampling_rate, f_qt[0])
        if f_qt is not None:
            with open(f_qt[0], 'w') as f:
                f.write(script)
            with open(f_qt[0] + ".data", 'wb') as f:
                self.spectrum.tofile(f)

    @Slot()
    def export_python_spectrum(self):
        f_qt = QFileDialog.getSaveFileName(self, 'Save', filter='*.py')
        script = export_fd.make_numpy(self.params, self.new_sampling_rate, f_qt[0])
        if f_qt is not None:
            with open(f_qt[0], 'w') as f:
                f.write(script)
            with open(f_qt[0] + ".data", 'wb') as f:
                self.spectrum.tofile(f)
        
    @Slot()
    def view_spectrum_slot(self):
        signal = 10 * np.log10(self.spectrum)
        signal = downsample_for_display(signal)
        new_plot = Plotter((self.new_sampling_rate / 2) * np.arange(len(signal)) / len(signal), signal)
        new_plot.closed.connect(self.parent_().plot_closed_slot)
        self.parent_().plots.append(new_plot)
        
    @Slot()
    def peak_detection_slot(self):
        if len(self.spectrum) < 3000:
            msgBox = QMessageBox()
            msgBox.setText("Estimated spectrum vector is too short. Please choose a higher interpolation factor.")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()
        else:
            self.pd_worker = PeakDetectionWorker.PeakDetectionWorker(self.spectrum, self.new_sampling_rate)
            self.pd_thread = QThread()
            self.pd_worker.moveToThread(self.pd_thread)
            self.pd_worker.done.connect(self.pd_done_slot)
            self.pd_thread.started.connect(self.pd_worker.do_processing)
            self.pd_thread.start()
            self.pd_worker.done.connect(self.pd_thread.quit)
            self.pd_thread.finished.connect(self.pd_thread.deleteLater)
        
    @Slot(np.ndarray, np.ndarray, np.ndarray)
    def pd_done_slot(self, sig, x_snr, snr):
        f_scale = self.new_sampling_rate * np.arange(len(sig)) / 2 / len(sig)
        fig = plt.figure()
        fig.subplots_adjust(hspace=0.5)
        ax = fig.add_subplot(211)
        ax.plot(f_scale, sig)
        plt.ylabel("PSD")
            
        ax = fig.add_subplot(212)
        ax.stem(x_snr, snr)
        plt.ylabel("SNR")
        plt.xlabel("Frequency (Hz)")
        plt.show()
       
        
    @Slot()
    def next_slot_estim(self):
        self.params.update({
                                'method' : self.hosted_widget.estimation_methods[self.hosted_widget.method_combo.currentIndex()],
                                'do_interpol' : self.hosted_widget.interpolate_chkbx.isChecked(),
                                'interpol_factor' : float(self.hosted_widget.interpolate_edit.text()),
                                'parameter' : int(self.hosted_widget.parameter_edit.text()),
                                'window' : windowing.windows[self.hosted_widget.window_list[self.hosted_widget.window_combo.currentIndex()]],
                                'fix_power' : self.hosted_widget.powerfix_chkbx.isChecked()
                            })
        
        self.processing_worker = ProcessingWorker(self.signal, self.params)
        self.processing_worker.update_message.connect(self.progress_label.setText)
        self.processing_worker.done.connect(self.processing_done_slot)
        self.process_thread = QThread()
        self.processing_worker.moveToThread(self.process_thread)
        self.process_thread.started.connect(self.processing_worker.do_processing)
        self.processing_worker.done.connect(self.process_thread.quit)
        self.process_thread.finished.connect(self.process_thread.deleteLater)
        self.process_thread.start()
        
        self.progress_header_label.setText('<h4>Performing spectral analysis</h4>')
        self.progress_bar.setMinimum(0)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(0)
        self.progress_label.setVisible(False)
        self.hosted_widget.setVisible(False)
        self.header_title_label.setVisible(False)
        self.cancel_button.setVisible(False)
        self.next_button.setVisible(False)
        
        self.signal = None
        
    def closeEvent(self, *args, **kwargs):
        try:
            self.process_thread.stop()
            self.process_thread.wait()
            self.preprocess_thread.stop()
            self.preprocess_thread.wait()
            self.pd_thread.stop()
            self.pd_thread.wait()
        except AttributeError:
            pass
        self.closed.emit(self)
        

class DomainConfigWidget(QWidget):
    
    title = "<h3>Step 1: Configure preprocessing options</h3>"
    
    
    def __init__(self, parent_):
        QWidget.__init__(self)
        
        self.parent_ = weakref.ref(parent_)
        
        self.main_vbox = QVBoxLayout(self)
        self.main_vbox.setAlignment(Qt.AlignTop)
        self.main_vbox.setContentsMargins(0, 0, 0, 0)
        
        self.date_hbox = QHBoxLayout(self)
        self.main_vbox.addLayout(self.date_hbox)
        start_date_label = QLabel('Start time:')
        self.date_hbox.addWidget(start_date_label)
        self.start_date_dateedit = STDateTimeEdit()
        self.start_date_dateedit.setMinimumDateTime(QDateTime(config.db[self.parent_().files[0]]['start_time']))
        self.start_date_dateedit.setMaximumDateTime(QDateTime(config.db[self.parent_().files[0]]['end_time']))
        self.start_date_dateedit.setDateTime(QDateTime(config.db[self.parent_().files[0]]['start_time']))
        self.date_hbox.addWidget(self.start_date_dateedit)
        self.date_hbox.addSpacing(10)
        end_date_label = QLabel('End time:')
        self.date_hbox.addWidget(end_date_label)
        self.end_date_dateedit = STDateTimeEdit()
        self.end_date_dateedit.setMinimumDateTime(QDateTime(config.db[self.parent_().files[-1]]['start_time']))
        self.end_date_dateedit.setMaximumDateTime(QDateTime(config.db[self.parent_().files[-1]]['end_time']))
        self.end_date_dateedit.setDateTime(QDateTime(config.db[self.parent_().files[-1]]['end_time']))
        self.date_hbox.addWidget(self.end_date_dateedit)
        
        
        self.frequency_hbox = QHBoxLayout()
        self.main_vbox.addLayout(self.frequency_hbox)
        self.max_freq_label = QLabel('Maximum frequency of interest:')
        self.frequency_hbox.addWidget(self.max_freq_label)
        self.max_freq_edit = QLineEdit('' + str(config.db[self.parent_().files[0]]['sampling_rate'] / 2))
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
        
    def get_params(self):
        return  {   
                 'start_time': self.start_date_dateedit.date(),
                 'end_time': self.end_date_dateedit.date(),
                 'max_frequency' : float(self.max_freq_edit.text()),
                 'do_whitening' : self.whitening_chkbx.isChecked(),
                 'whitening_order' : int(self.whitening_order_spinner.value()),
                 'fix_discontinuities' : self.discontinuity_chkbx.isChecked()
                }
        
    @Slot()
    def whitening_slot(self):
        self.whitening_order_spinner.setEnabled(self.whitening_chkbx.isChecked())
        
        
class EstimationConfigWidget(QWidget):
    
    title = "<h3>Step 2: Configure estimation parameters</h3>"
    
    estimation_methods = ['Periodogram', 'Bartlett', 'Welch', 'Auto-regressive modeling']
    estimation_methods_params = ['', 'Number of segments', 'Segment length', 'Number of poles']
    
    def __init__(self, parent_):
        QWidget.__init__(self)
        
        self.parent_ = weakref.ref(parent_)
        
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
        self.method_combo.currentIndexChanged.connect(self.update_info_table)
        self.method_combo.addItems(self.estimation_methods)
        self.method_hbox.addWidget(self.method_combo)
        
        self.window_hbox = QHBoxLayout()
        self.left_vbox.addLayout(self.window_hbox)
        self.window_label = QLabel('Data window')
        self.window_hbox.addWidget(self.window_label)
        self.window_combo = QComboBox()
        self.window_list = windowing.windows.keys()
        self.window_combo.currentIndexChanged.connect(self.update_info_table)
        self.window_combo.addItems(self.window_list)
        self.window_hbox.addWidget(self.window_combo)
        
        self.interpolate_hbox = QHBoxLayout()
        self.left_vbox.addLayout(self.interpolate_hbox)
        self.interpolate_chkbx = QCheckBox('Interpolate estimated spectrum')
        self.interpolate_hbox.addWidget(self.interpolate_chkbx)
        self.interpolate_edit = QLineEdit('1.0')
        self.interpolate_hbox.addStretch()
        self.interpolate_hbox.addWidget(self.interpolate_edit)
        
        self.powerfix_hbox = QHBoxLayout()
        self.left_vbox.addLayout(self.powerfix_hbox)
        self.powerfix_chkbx = QCheckBox('Restore signal power')
        self.powerfix_hbox.addWidget(self.powerfix_chkbx)
        
        
        self.parameter_hbox = QHBoxLayout()
        self.left_vbox.addLayout(self.parameter_hbox)
        self.parameter_label = QLabel('Number of segments:')
        self.parameter_hbox.addWidget(self.parameter_label)
        self.parameter_edit = QLineEdit('2')
        self.parameter_edit.textChanged.connect(self.update_info_table)
        self.parameter_edit.setEnabled(False)
        self.parameter_hbox.addStretch()
        self.parameter_hbox.addWidget(self.parameter_edit)
        
        self.left_vbox.addStretch()
        
        
        self.right_vbox = QVBoxLayout()
        self.main_hbox.addLayout(self.right_vbox)
        self.main_hbox.setStretchFactor(self.left_vbox, 2)
        self.info_table = QTableWidget(4, 2)
        self.right_vbox.addWidget(self.info_table)
        
        verthead = self.info_table.verticalHeader()
        verthead.setDefaultSectionSize(verthead.fontMetrics().height() + 4)
        verthead.hide()
         
        self.info_table.horizontalHeader().setStretchLastSection(True)
        
        self.info_table.horizontalHeader().hide()
        
        items = ['Sampling rate', 'Number of samples',
                 '3dB Bandwidth', 'Side lobe attenuation']
        for idx, val in enumerate(items):
            self.info_table.setItem(idx, 0, QTableWidgetItem(val))
        
        self.update_info_table()
        
        
    @Slot()
    def update_info_table(self):
        if hasattr(self.parent_(), 'new_sampling_rate'):
            bw = windowing.bw[self.window_list[self.window_combo.currentIndex()]]
            self.info_table.setItem(0, 1, QTableWidgetItem(frequency_fmt(self.parent_().new_sampling_rate)))
            sample_count = len(self.parent_().signal)
            self.info_table.setItem(1, 1, QTableWidgetItem(str(sample_count)))
            max_frequency_resolution = self.parent_().new_sampling_rate * bw / sample_count
            if self.method_combo.currentIndex() == 1:
                max_frequency_resolution *= int(self.parameter_edit.text())
            if self.method_combo.currentIndex() == 2:
                max_frequency_resolution = self.parent_().new_sampling_rate * bw / int(self.parameter_edit.text())
            if self.method_combo.currentIndex() == 3:
                self.info_table.setItem(2, 1, QTableWidgetItem('n.a.'))
            else:
                self.info_table.setItem(2, 1, QTableWidgetItem(frequency_fmt(max_frequency_resolution)))
            
        if hasattr(self, 'info_table'):
            self.info_table.setItem(3, 1, QTableWidgetItem(windowing.attenuation[self.window_list[self.window_combo.currentIndex()]]))
            self.info_table.resizeColumnsToContents()
        
        
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
        
